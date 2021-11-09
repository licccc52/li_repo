import React from 'react'
import {FormControl, InputLabel, Select} from '@material-ui/core'


export default class LanguagesSelect extends React.Component {
    render() {
        const language_option = Object.keys(this.props.languages)
            .map((language_code) => {
                return (<option value={language_code}>{this.props.languages[language_code]}</option>)
            });
        return (
            <FormControl variant="outlined" fullWidth size={'small'}>
                <InputLabel htmlFor="outlined-age-native-simple"> Select language</InputLabel>
                <Select
                    native
                    value={this.props.language}
                    onChange={this.props.changeLanguage}
                    inputProps={{
                        name: 'Language',
                        id: 'outlined-age-native-simple',
                    }}
                    size="small"
                >
                    {language_option}
                </Select>
            </FormControl>
        )
    }
}
