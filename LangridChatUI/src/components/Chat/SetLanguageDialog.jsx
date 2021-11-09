import React from 'react'
import {
    Dialog,
    DialogContent,
    FormControlLabel, Radio,
    RadioGroup,
    Typography,
    withStyles
} from "@material-ui/core";

const styles = (theme) => ({});

class SetLanguageDialog extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            open: false,
        }
    }

    handleChangeLanguage = (e) => {
        this.props.handleChangeLanguage(e.target.value)
        this.setState({open: false})
    }

    handleClickOpen = () => {
        this.setState({open: true})
    }

    handleClose = () => {
        this.setState({open: false})
    }

    render() {
        const {open} = this.state
        const {supportLanguages, userInfo} = this.props
        return (
            <div>
                <Typography onClick={this.handleClickOpen}>{supportLanguages[userInfo.language]}</Typography>
                <Dialog open={open} onClose={this.handleClose}>
                    <DialogContent>
                        <RadioGroup value={userInfo.language} onChange={this.handleChangeLanguage}>
                            {Object.keys(supportLanguages).map((language_code) => (
                                <FormControlLabel value={language_code} control={<Radio/>}
                                                  label={supportLanguages[language_code]}/>
                            ))}
                        </RadioGroup>
                    </DialogContent>
                </Dialog>
            </div>
        )
    }
}

export default withStyles(styles)(SetLanguageDialog)
