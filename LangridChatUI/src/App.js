import React from 'react';
import {BrowserRouter, Redirect, Route, Switch} from "react-router-dom";
import Chat from "./components/Chat/chat";
import SetUserInfo from "./components/SetUserInfo/SetUserInfo";


export default class App extends React.Component {
    render() {
        //{position: 'absolute', bottom: 0, height: '100%', width:'99%'}
        return (
            <BrowserRouter>
                <Switch>
                    <Route exact path="/langridchat" component={SetUserInfo}/>
                    <Route path="/langridchat/chat" component={Chat}/>
                    <Route path="/langridchat/:roomId" component={SetUserInfo}/>
                    <Redirect to='/langridchat'/>
                </Switch>
            </BrowserRouter>
        )
    }
};
