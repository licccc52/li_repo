import React from 'react'
import {List, ListItem, ListItemText, withStyles} from "@material-ui/core";
import styles from "../../css/Chat/OnlineUsers";
import {Lens} from "@material-ui/icons"
import {teal} from '@material-ui/core/colors'

class OnlineUsers extends React.Component {
    render() {
        const onLineColor = teal[500]
        const {classes} = this.props
        const userList = this.props.userList.map((user) => (
            <ListItem>
                <Lens style={{color: onLineColor, fontSize: "x-small", marginRight: '5%'}}/>
                <ListItemText primary={user}/>
            </ListItem>
        ))
        return (
            <div className={classes.userList}>
                <List dense={true}>
                    {userList}
                </List>
            </div>
        )
    }
}

export default withStyles(styles)(OnlineUsers)