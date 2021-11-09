import React from 'react';
import {Grid, IconButton, TextField} from "@material-ui/core";
import {Send} from "@material-ui/icons"

export default class ChatInput extends React.Component {

    handleTextChange = (e) => {
        this.props.changeMessage(e);
    };

    handleKeyDown = (e) => {
        if (e.keyCode === 13 && (e.ctrlKey || e.metaKey)) {
            this.props.sendMessage(e);
        }
    };

    render() {
        return (
            <Grid container xs={12}>
                <Grid item xs={11}>
                    <TextField
                        multiline
                        rowsMax={2}
                        value={this.props.message}
                        onChange={this.handleTextChange}
                        onKeyDown={this.handleKeyDown}
                        onFocus={this.props.startTyping}
                        onBlur={this.props.endTyping}
                        id="outlined-size-small"
                        variant="outlined"
                        size="small"
                        fullWidth
                    />
                </Grid>
                <Grid item xs={1}>
                    <IconButton onClick={this.props.sendMessage}>
                        <Send/>
                    </IconButton>
                </Grid>
            </Grid>
        )
    }
}
