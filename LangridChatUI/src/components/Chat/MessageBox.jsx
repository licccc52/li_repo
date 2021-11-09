import React from "react";
import {Grid, TextField} from "@material-ui/core";


export default class MessageBox extends React.Component {
    constructor(props) {
        super(props);
        this.childDiv = React.createRef()
    }

    componentDidMount = () => this.handleScroll();

    componentDidUpdate = () => this.handleScroll();

    handleScroll = () => {
        document.getElementById('ScrollToBottom').scrollIntoView({behavior: 'smooth', block: 'end'})
    };

    render() {
        return (
            <Grid item xs={12} style={{height: '100%', overflowY: 'auto'}}>
                {
                    this.props.messageList.map((item) => {
                        const isSender = this.props.userInfo.name === item.sender;
                        return (
                            <Grid container direction="row"
                                  justify={isSender ? "flex-end" : "flex-start"}
                                  alignItems="flex-end">
                                <Grid item xs={10} md={8}>
                                    <p/>
                                    <TextField
                                        multiline
                                        id="outlined-read-only-input"
                                        label={item.sender + '　' + item.time + '　' + this.props.languages[item.language]}
                                        value={this.props.userInfo.language === item.language ?
                                            item.message :
                                            item.translations[this.props.userInfo.language]}
                                        InputProps={{
                                            readOnly: true,
                                        }}
                                        variant="outlined"
                                        size="small"
                                        fullWidth
                                    />
                                </Grid>
                            </Grid>
                        )
                    })
                }
                <div id={"ScrollToBottom"}>
                </div>
            </Grid>
        )
    }
}
