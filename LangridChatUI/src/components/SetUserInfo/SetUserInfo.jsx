import React from 'react';
import {Button, FormControlLabel, Grid, Switch, TextField, withStyles} from "@material-ui/core";
import LanguagesSelect from "./LanguagesSelect";
import client from "../../config/ApiClient";
import styles from "../../css/SetUserInfo/common";


class SetUserInfo extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            languages: {ja: '日本語'},
            language: 'ja',
            isCreateRoom: false,
            room: '',
            name: Math.floor(Math.random() * 1000)
        }
    }

    componentWillMount() {
        client
            .get('/support-language')
            .then(response => {
                this.setState(() => ({
                    languages: response.data
                }))
            })
        if (this.props.match.params.hasOwnProperty('roomId')) {
            console.log(this.props.match)
            this.setState({room: this.props.match.params.roomId})
        }
    };

    handleChangeRoom = e => {
        this.setState({room: e.target.value})
    };

    handleChangeName = e => {
        this.setState({name: e.target.value})
    };

    handleChangeLanguage = e => {
        this.setState({language: e.target.value})
    };

    handleChangeSwitch = e => {
        this.setState({isCreateRoom: e.target.checked})
    };

    handleClick = () => {
        const isCreateRoom = this.state.isCreateRoom, room = this.state.room;
        const redirectToChat = (response) => {
            this.props.history.push({
                pathname: '/langridchat/chat',
                query: {
                    name: this.state.name,
                    language: this.state.language,
                    room: response.data.room,
                    languages: this.state.languages
                }
            })
        };

        if (!isCreateRoom && room) {
            client
                .get('/room/' + room + '/')
                .then(redirectToChat)
                .catch((error) => {
                    window.confirm(error)
                });
        } else if (isCreateRoom) {
            client
                .post('/room/')
                .then((response) => {
                    window.confirm('room name: ' + response.data.room);
                    redirectToChat(response)
                })
                .catch((error) => {
                    window.confirm(error)
                });
        }
    };

    render() {
        const {classes} = this.props;
        const isCreateRoom = this.state.isCreateRoom;
        return (
            <Grid container
                  direction="row"
                  justify="center"
                  alignItems="center"
                  spacing={0}
                  className={classes.root}
                  style={{padding: '10px', height: '100%'}}
            >
                <Grid item xs={12} md={10} lg={7}>
                    <Grid container
                          direction="row"
                          justify="center"
                          alignItems="center"
                          spacing={1}
                          style={{height: '99%', width: '100%'}}
                    >
                        {isCreateRoom ?
                            '' :
                            <Grid item xs={12}>
                                <TextField id="outlined-basic"
                                           label="Room"
                                           variant="outlined"
                                           value={this.state.room}
                                           onChange={this.handleChangeRoom}
                                           size="small"
                                           fullWidth
                                />
                            </Grid>
                        }
                        <Grid item xs={12} md={6} lg={7} style={{width: '100%'}}>
                            <TextField id="outlined-basic"
                                       label="Input your nick name"
                                       variant="outlined"
                                       onChange={this.handleChangeName}
                                       size="small"
                                       fullWidth
                            />
                        </Grid>
                        <Grid item xs={12} md={2}>
                            <LanguagesSelect
                                language={this.state.language}
                                languages={this.state.languages}
                                changeLanguage={this.handleChangeLanguage}
                            />
                        </Grid>
                        <Grid item xs={12} md={3}>
                            <Button variant="contained"
                                    color="primary"
                                    onClick={this.handleClick}
                                    fullWidth
                            >
                                {isCreateRoom ? 'CREATE ROOM' : 'JOIN ROOM'}
                            </Button>
                        </Grid>
                    </Grid>
                    <Grid item xs={12}>
                        <FormControlLabel value={true}
                                          control={<Switch checked={isCreateRoom}
                                                           onChange={this.handleChangeSwitch}
                                                           color="primary"/>}
                                          label='you also can create new room：' labelPlacement="start"/>
                    </Grid>
                </Grid>
            </Grid>
        )
    }
}

export default withStyles(styles)(SetUserInfo)
