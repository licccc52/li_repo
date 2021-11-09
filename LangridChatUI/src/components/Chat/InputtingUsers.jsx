import React from 'react';
import {Grid, withStyles} from "@material-ui/core";
import styles from "../../css/Chat/InputtingUsers";


class InputtingUsers extends React.Component {
    render() {
        const {classes, inputtingUsers} = this.props
        return (
            <Grid xs={12} className={classes.inputtingUsers}>
                {(JSON.stringify(inputtingUsers) === '[]') ? null : 'Inputting users: ' + inputtingUsers.join()}
            </Grid>
        )
    }

}

export default withStyles(styles)(InputtingUsers)