# chat/consumers.py
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from langrid.TranslationClient import GoogleClient, SupportLanguages
from .models import Message, Room, TranslateMessage, User
import threading
# 要約機能

from pysummarization.nlpbase.auto_abstractor import AutoAbstractor
from pysummarization.tokenizabledoc.mecab_tokenizer import MeCabTokenizer
from pysummarization.abstractabledoc.top_n_rank_abstractor import TopNRankAbstractor
from pysummarization.nlp_base import NlpBase
from pysummarization.similarityfilter.tfidf_cosine import TfIdfCosine

# 单文要约机能
import itertools
import joblib
import networkx as nx
import nltk
import numpy as np
import re
import spacy
from functools import reduce
from spacy.lang.ja import TAG_MAP

# 日本語文区切り
import functools
from ja_sentence_segmenter.common.pipeline import make_pipeline
from ja_sentence_segmenter.concatenate.simple_concatenator import concatenate_matching
from ja_sentence_segmenter.normalize.neologd_normalizer import normalize
from ja_sentence_segmenter.split.simple_splitter import split_newline, split_punctuation

#make table
from tabulate import tabulate

def ja_spliter(sen):
    split_punc2 = functools.partial(split_punctuation, punctuations=r"。!? . 　．")
    concat_tail_no = functools.partial(concatenate_matching, former_matching_rule=r"^(?P<result>.+)(の)$",
                                       remove_former_matched=False)
    segmenter = make_pipeline(normalize, split_newline, concat_tail_no, split_punc2)
    return (list(segmenter(sen)))

nlp = spacy.load("ja_core_news_sm")
edge_model = joblib.load("edge_model.joblib")
context_vectorizer = joblib.load("context_vectorizer.joblib")
cfdist = joblib.load("cfdist.joblib")
compression_model = joblib.load("compression_model.joblib")
regression_vectorizer = joblib.load("regression_vectorizer.joblib")

def nbor(token, offset):
    try:
        nbor = token.nbor(offset)
        return nbor
    except:
        return None


def pos(token):
    if token:
        return token.pos_
    return "None"


def matching_head(token):
    l, r = -1, 1
    matching_heads = {token: 1}
    while True:
        if nbor(token, l):
            matching_heads[nbor(token, l)] = int(token.head == token.nbor(l).head)
            l -= 1
        else:
            break
    while True:
        if nbor(token, r):
            matching_heads[nbor(token, r)] = int(token.head == token.nbor(r).head)
            r += 1
        else:
            break
    return matching_heads


def context(e):
    V = {}
    V["0_dep"] = e.dep_
    V["1_head_pos"] = e.head.pos_
    V["2_modifier"] = e.pos_
    V["4_head_head_pos"] = e.head.head.pos_
    V["5_head_dep"] = e.head.dep_
    V["6_-3_head_pos"] = pos(nbor(e.head, -3)) # e.head.l.l.l.pos_
    V["7_-2_head_pos"] = pos(nbor(e.head, -2)) # e.head.l.l.pos_
    V["8_-1_head_pos"] = pos(nbor(e.head.i, -1)) # e.head.l.pos_
    V["9_+1_head_pos"] = pos(nbor(e.head, 1)) # e.head.r.pos_
    V["10_+2_head_pos"] = pos(nbor(e.head, 2)) # e.head.r.r.pos_
    V["11_+3_head_pos"] = pos(nbor(e.head, 3)) # e.head.r.r.r.pos_
    V["12_-3_modifier_pos"] = pos(nbor(e, -3)) # e.l.l.l.pos_
    V["13_-2_modifier_pos"] = pos(nbor(e, -2)) # e.l.l.pos_
    V["14_-1_modifier_pos"] = pos(nbor(e, -1)) # e.l.pos_
    V["15_+1_modifier_pos"] = pos(nbor(e, 1)) # e.r.pos_
    V["16_+2_modifier_pos"] = pos(nbor(e, 2)) # e.r.r.pos_
    V["17_+3_modifier_pos"] = pos(nbor(e, 3)) # e.r.r.r.pos_
    return V


def get_root(doc):
    sent = next(doc.sents, None)
    return sent.root if sent is not None else sent


def get_edge_probs(edge_model, vectorizer, edge):
    return list(zip(edge_model.classes_,
                    edge_model.predict_proba(vectorizer
                                             .transform(context(edge)))[0]))


def get_probs(edge_model, vectorizer, edge, threshold=0.2):
    probs = get_edge_probs(edge_model, vectorizer, edge)
    filtered_probs = [p for p in probs if p[1] > threshold]
    return filtered_probs


def get_groups(edge_model, vectorizer, doc):
    return [[(d, p[0]) for p in get_probs(edge_model, vectorizer, d)]
            for d in doc]


def get_possible_paths(groups):
    return list(itertools.product(*groups))


def generate_candidate_compressions(nlp, edge_model, vectorizer, sentence):
    doc = nlp(sentence)
    root = get_root(doc)
    groups = get_groups(edge_model, vectorizer, doc)
    candidates = set()
    for path in get_possible_paths(groups):
        path_graph = nx.DiGraph()
        for edge, label in path:
            path_graph.add_edge(edge.head.i, edge.i)
        for head, modifier in list(nx.edge_bfs(path_graph, root.i)):
            label = [l for e, l in path if e.i == modifier][0]
            if path_graph.has_node(modifier) and label == "del_l":
                subtree = list(nx.edge_bfs(path_graph, modifier))
                path_graph.remove_edges_from([(head, modifier), *subtree])
            elif path_graph.has_node(modifier) and label == "del_u":
                subtree = list(nx.edge_bfs(path_graph, modifier))
                path_graph = nx.DiGraph()
                path_graph.add_edges_from(subtree)
        if len(path_graph.edges) > 0:
            candidates.add(" ".join([doc[n].text
                                     for n
                                     in sorted(list(set([n
                                                         for e
                                                         in path_graph.edges
                                                         for n
                                                         in e])))]))
    return candidates


def match(uncomp, comp):
    uncomp_indicies = [i for i in range(len(uncomp))]
    comp_indicies = []
    uncomp_w, comp_w = 0, 0
    while uncomp_w < len(uncomp) and comp_w < len(comp):
        if uncomp[uncomp_w] == comp[comp_w]:
            comp_indicies.append(uncomp_w)
            comp_w += 1
        uncomp_w += 1
    return comp_indicies


def POS_features(s, c):
    doc = nlp(" ".join(s))
    s_indices = set([i for i in range(len(s))])
    c_indices = set(match(s, c))
    c_deletions = s_indices - c_indices
    uncomp_doc = [token.tag_ for token in doc]
    del_doc = [token.tag_ for token in doc if token.i in c_deletions]
    pos_feat = {}
    for pos in list(TAG_MAP.keys()):
        pos_feat[pos + "_UNCOMP"] = uncomp_doc.count(pos)
        pos_feat[pos + "_DEL"] = del_doc.count(pos)
    return pos_feat


def Gramm(c, cfdist):
    m = len(c)
    if m > 2:
        likelihood_candidate = reduce(lambda x, y: x*y, [cfdist[(t1, t2)].freq(t3) for t1, t2, t3 in nltk.trigrams(c)])
    elif m == 0:
        return 0
    else:
        likelihood_candidate = 0
    return (1 / m) * np.log(1 + likelihood_candidate) #+1 backoff


def get_regression_features(uncomp_tok, curr_tok):
    features = {
        "grammaticality_rate": Gramm(curr_tok, cfdist),
        # "importance_rate": Imp_Rate(D, uncomp_tok, curr_tok),
        # "average_deletion_depth": average_deletion_depth(uncomp_tok, curr_tok),
        # "average_inclusion_depth": average_inclusion_depth(uncomp_tok, curr_tok)
    }
    features.update(POS_features(uncomp_tok, curr_tok))
    return features

def slpcompress(sentence):
    try:
        end = ""
        if sentence is None or sentence == "" or sentence == ". 　．":
            return {"if err"}

        if re.match("\W", sentence[-1]):
            end = sentence[-1]
            sentence = sentence[:-1]
        candidate_compressions = generate_candidate_compressions(nlp,
                                                                edge_model,
                                                                context_vectorizer,
                                                                sentence)
        ret = list(zip([f"{n}   {c}{end}" for n, c in enumerate(candidate_compressions)]))[:3]
        ret.append('@')
        return ret

    except Exception as e:
        return {f" error: {e}"}

def pysum(sen):

    nlp_base = NlpBase()
    # トークナイザーを設定します。 これは、MeCabを使用した日本語のトークナイザーです
    nlp_base.tokenizable_doc = MeCabTokenizer()
    # 「類似性フィルター」のオブジェクト。 このオブジェクトによって観察される類似性は、Tf-Idfベクトルのいわゆるコサイン類似性です
    similarity_filter = TfIdfCosine()
    # NLPのオブジェクトを設定します
    similarity_filter.nlp_base = nlp_base
    # 類似性がこの値を超えると、文は切り捨てられます
    similarity_filter.similarity_limit = 0.2
    # 自動要約のオブジェクト    自动汇总对象
    auto_abstractor = AutoAbstractor()
    # 日本語のトークナイザーを設定   日语 标记
    auto_abstractor.tokenizable_doc = MeCabTokenizer()
    # ドキュメントを抽象化およびフィルタリングするオブジェクト   提取和过滤文档的对象
    abstractable_doc = TopNRankAbstractor()
    result_dict = auto_abstractor.summarize(sen, abstractable_doc, similarity_filter)
    output = str()
    for sentence in result_dict["summarize_result"]:
        output = output + str(sentence)

    return output


class ChatConsumer(AsyncJsonWebsocketConsumer):
    room_name: str
    room_group_name: str
    user_name: str
    room: Room
    user: User

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.user_name = self.scope['url_route']['kwargs']['user_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.room, create = await database_sync_to_async(Room.objects.get_or_create)(room=self.room_name)
        self.user, create = await database_sync_to_async(User.objects.get_or_create)(name=self.user_name)

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        await self.join_room()

    async def disconnect(self, close_code):
        await self.end_typing()
        await self.leave_room()
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive_json(self, content, **kwargs):
        command = content.get('command', None)

        try:
            if command == 'translation':
                await self.translation_message(content['event'])
            elif command == 'start_typing':
                await self.start_typing()
            elif command == 'end_typing':
                await self.end_typing()
        except BaseException as e:
            raise e

    async def translation_message(self, event):
        """
        :param event: type<'dir'>
                event should like {
                    'message': type<'str'>,
                    'language': type<'str'>,
                    'sender': type<'any'>
                    }
        :return: Will respond json which is like
                            {
                            type: 'chat_message',
                            message: "こんにちは",
                            language: "ja",
                            sender: 337,
                            translations: {
                                zh: "您好",
                                en: "Hello"
                                }
                            }
        """
        target_language_list = list(SupportLanguages.keys())
        target_language_list.remove(event['language'])
        translations = {}   # 翻译后的文本

        # def translate_messages(source, target, source_message):
        #     translations[target] = str(GoogleClient.translate(source, target, source_message))
        def translate_messages(source, target, source_message, output=list(),output2=list()):
            if source == 'ja' and target == 'ko':
                translations[target] = str(pysum(source_message))
            elif source == 'ja' and target == 'es':
                out = ja_spliter(source_message)
                for sen in out:
                    output.extend(slpcompress(sen))
                translations[target] = tabulate(output, headers=["番号 短縮結果"])
            elif source == 'ja' and target == 'ne':
                mix = pysum(source_message)
                sent = ja_spliter(mix)
                for sen in sent:
                    output2.extend(slpcompress(sen))
                mix2 = tabulate(output2, headers=["番号 短縮結果"])
                translations[target] = mix2
            else:
                translations[target] = str(GoogleClient.translate(source, target, source_message))

        for tg_lang in target_language_list:
            t = threading.Thread(target=translate_messages, args=(event['language'], tg_lang, event['message']))
            t.start()
            t.join()
        event['translations'] = translations
        event['sender'] = self.user.name

        message = await self.save_message(event)
        event['message_primary_key'] = message.pk
        event['time'] = message.created_time.strftime('%b, %d %H:%M')
        event['type'] = 'chat_message'
        await self.channel_layer.group_send(self.room_group_name, event)

    async def join_room(self):
        await self.set_online_user()
        event = {
            'type': 'online_users',
            'users': [user.name for user in await self.get_online_users()]
        }
        await self.channel_layer.group_send(self.room_group_name, event)

    async def leave_room(self):
        await self.set_online_user(remove=True)
        event = {
            'type': 'online_users',
            'users': [user.name for user in await self.get_online_users()]
        }
        await self.channel_layer.group_send(self.room_group_name, event)

    async def start_typing(self):
        """
        :return: { type: 'inputting_users', users: type<'list'> }
        """
        await self.set_typing_user()
        event = {
            'type': 'inputting_users',
            'users': [user.name for user in await self.get_typing_users()]
        }
        await self.channel_layer.group_send(self.room_group_name, event)

    async def end_typing(self):
        """
        :return: { type: 'inputting_users', users: type<'list'> }
        """
        await self.set_typing_user(remove=True)
        event = {
            'type': 'inputting_users',
            'users': [user.name for user in await self.get_typing_users()]
        }
        await self.channel_layer.group_send(self.room_group_name, event)

    async def online_users(self, event: dict):
        await self.send_json({
            'type': 'online_users',
            'users': event['users']
        })

    async def inputting_users(self, event: dict):
        """
        :param event: { 'type': 'inputting_users', 'users': type<'List'> }
        """
        await self.send_json({
            'type': 'inputting_users',
            'users': event['users']
        })

    async def chat_message(self, event: dict):
        """
        Clientにメッセージを送信
        :param event: dict
        """

        # 受信者を記録
        self.set_message_addressee(event.get('message_primary_key'))

        # Clientに送信
        await self.send_json({
            'type': 'chat_message',
            'message': event.get('message'),
            'language': event.get('language'),
            'sender': event.get('sender'),
            'translations': event.get('translations'),
            'time': event.get('time')
        })

    @database_sync_to_async
    def save_message(self, event: dict):
        """
        メッセージと訳文をデータベースに書き込み
        :param event: dict
        :return: Message's primary key
        """
        chat_message = Message.objects.create(sender=self.user, room=self.room,
                                              message=event.get('message'), language=event.get('language'))
        for language, message in event.get('translations').items():
            TranslateMessage.objects.create(source=chat_message, language=language, message=message)
        return chat_message

    @database_sync_to_async
    def set_message_addressee(self, primary_key: Message):
        """
        現在ユーザーをメッセージの受信者として追加
        :param primary_key: Message's primary key
        """
        Message.objects.get(pk=primary_key).addressees.add(self.user)

    @database_sync_to_async
    def get_message(self, pk):
        return Message.objects.get(pk=pk)

    @database_sync_to_async
    def set_online_user(self, remove=False):
        if remove:
            self.room.online.remove(self.user)
        else:
            self.room.online.add(self.user)
            # Room.objects.get(pk=self.room.id).online.add(self.user)
            # print(self.room.online.all())

    @database_sync_to_async
    def get_online_users(self):
        users = Room.objects.get(pk=self.room.id).online.all()
        return [user for user in users]

    @database_sync_to_async
    def set_typing_user(self, remove=False):
        if remove:
            self.room.typing.remove(self.user)
        else:
            self.room.typing.add(self.user)

    @database_sync_to_async
    def get_typing_users(self):
        return [user for user in self.room.typing.all()]
