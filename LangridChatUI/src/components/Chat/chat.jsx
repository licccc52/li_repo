import React from 'react'
import clsx from 'clsx'
import {
    AppBar,
    Divider,
    Drawer,
    Grid,
    IconButton,
    Toolbar,
    Typography,
    withStyles,
    withTheme,
} from "@material-ui/core";
import {ChevronLeft, ChevronRight} from "@material-ui/icons";
import MenuIcon from '@material-ui/icons/Menu';
import MessageBox from "./MessageBox";
import ChatInput from "./chatInput";
import styles from "../../css/Chat/common";
import SetLanguageDialog from "./SetLanguageDialog";
import InputtingUsers from "./InputtingUsers";
import OnlineUsers from "./OnlineUsers";
import {CHAT_HOST} from "../../config/WebSocketClient";

class Chat extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            room: 'test room',
            socket: null,
            openDrawer: true,
            snackbar: {
                open: false,
                message: '',
            },
            userInfo: {
                name: '',
                language: ''
            },
            message: '',
            messageList: [],
            // messageList: [{
            //     message: '',
            //     sender: '',
            //     language: '',
            //     translations: {
            //         zh: '',
            //         en: ''
            //     },
            //     time: ''
            // }],
            inputtingUsers: [],
            onlineUsers: []
            // onlineUsers: [{
            //     name: 'Cuo',
            //     language: 'zh'
            // }]
        }
    }

    componentWillMount() {
        if (!this.props.location.hasOwnProperty('query')) {
            return this.props.history.push('/langridchat/');
        }
        const query = this.props.location.query;
        if (!query.hasOwnProperty('room') || !query.hasOwnProperty('name') || !query.hasOwnProperty('language') || !query.hasOwnProperty('languages')) {
            return this.props.history.push('/langridchat/');
        }
        this.setState(() => ({
            room: this.props.location.query.room,
            userInfo: {
                name: query.name,
                language: query.language
            }
        }))
    }

    componentDidMount() {
        const url = CHAT_HOST + `/${this.props.location.query.room}/${this.state.userInfo.name}/`;
        const socket = new WebSocket(url);
        this.setState(() => ({socket: socket}));
        socket.onmessage = (event) => {
            const response = JSON.parse(event.data);
            switch (response.type) {
                case 'chat_message':
                    this.chatMessage(response);
                    break;
                case 'server_response':
                    this.serverResponse(response);
                    break;
                case 'online_users':
                    this.onlineUsers(response);
                    break;
                case 'inputting_users':
                    this.inputtingUsers(response);
                    break;
                default:
                    console.log(response);
            }
        };
    }

    chatMessage = (response) => {
        delete response.type;
        console.log(response)
        this.setState((status) => {
            // status.messageList.unshift(response);
            return ({
                messageList: status.messageList.concat(response)
            })
        })
    };

    onlineUsers = (response) => {
        const {users} = response;
        this.setState({
            onlineUsers: users
        })
    }

    inputtingUsers = (response) => {
        const {users} = response;
        this.setState({
            inputtingUsers: users
        })
    }

    serverResponse = (response) => {
        this.showSnackBar(response);
    };


    showSnackBar = (message, vertical = 'bottom', horizontal = 'center', color = "info") => {
        this.setState({
            snackbar: {
                open: true,
                anchorOrigin: {vertical: vertical, horizontal: horizontal},
                message: message,
                color: color
            }
        })
    }

    handleDrawer = () => {
        this.setState((state) => ({
            openDrawer: !state.openDrawer
        }))
    }

    handleChangeLanguage = (language) => {
        this.setState((state) => {
            state.userInfo.language = language
            return {
                userInfo: state.userInfo
            }
        })
    };

    handleChangeMessage = (e) => {
        this.setState({message: e.target.value});
    };

    handleSendMessage = () => {
        if (!this.state.message) {
            this.showSnackBar('何かを入力してください');
            return null;
        }
        // send message
        this.state.socket.send(JSON.stringify({
            command: 'translation',
            event: {
                message: this.state.message,
                language: this.state.userInfo.language,
                sender: this.state.userInfo.name
            }
        }));

        // 发送消息后清空输入框
        this.setState({
            message: '',
        })
    }

    handleStartTyping = () => {
        this.state.socket.send(JSON.stringify({
            command: 'start_typing',
            event: {
                user: this.state.userInfo.name
            }
        }))
    }

    handleEndTyping = () => {
        this.state.socket.send(JSON.stringify({
            command: 'end_typing',
            event: {
                user: this.state.userInfo.name
            }
        }))
    }

    render() {
        const {languages} = this.props.location.query;
        const {classes, theme} = this.props;
        const {openDrawer} = this.state;

        return (
            <div className={classes.root}>
                <AppBar position="fixed" className={clsx(classes.appBar, {[classes.appBarShift]: openDrawer})}>
                    <Toolbar>
                        <Typography variant="h6" className={classes.roomId}>
                            {this.state.room}
                        </Typography>
                        <SetLanguageDialog
                            supportLanguages={languages}
                            userInfo={this.state.userInfo}
                            handleChangeLanguage={this.handleChangeLanguage}
                        />
                        <IconButton
                            edge="end"
                            color="inherit"
                            aria-label="open drawer"
                            onClick={this.handleDrawer}
                            className={clsx(openDrawer && classes.hide)}
                        >
                            <MenuIcon/>
                        </IconButton>
                    </Toolbar>
                </AppBar>
                <main className={clsx(classes.content, {[classes.contentShift]: openDrawer})}>
                    <Grid container
                          className={classes.chatBox}
                          direction="row"
                          justify="flex-end"
                          alignContent="center"
                    >
                        <Grid container
                              className={classes.messageBox}
                              direction="row"
                              justify="center"
                              alignItems="flex-end"
                        >
                            <div className={classes.drawerHeader}/>
                            <MessageBox
                                messageList={this.state.messageList}
                                languages={languages}
                                userInfo={this.state.userInfo}
                            />
                        </Grid>
                        <ChatInput
                            message={this.state.message}
                            changeMessage={this.handleChangeMessage}
                            sendMessage={this.handleSendMessage}
                            startTyping={this.handleStartTyping}
                            endTyping={this.handleEndTyping}
                        />
                        <InputtingUsers
                            inputtingUsers={this.state.inputtingUsers}
                        />
                    </Grid>
                </main>
                <Drawer
                    className={classes.drawer}
                    variant="persistent"
                    anchor="right"
                    open={openDrawer}
                    classes={{
                        paper: classes.drawerPaper,
                    }}
                >
                    <div className={classes.drawerHeader}>
                        <IconButton onClick={this.handleDrawer}>
                            {theme.direction === 'rtl' ? <ChevronLeft/> : <ChevronRight/>}
                        </IconButton>
                    </div>
                    <Divider/>
                    <OnlineUsers
                        userList={this.state.onlineUsers}
                    />
                </Drawer>
            </div>
        );
    }
}

export default withStyles(styles)(withTheme(Chat))
