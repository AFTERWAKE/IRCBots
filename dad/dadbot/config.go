package dad

import (
	"encoding/json"
	"io/ioutil"
	"os"
)

// ReadConfig reads each config file and returns a struct of each
func ReadConfig() (IRCConfig, DadConfig, MomConfig) {
	return readIrcConfig(), readDadConfig(), readMomConfig()
}

func readIrcConfig() IRCConfig {
	file, _ := os.Open(ircConfigFile)
	defer file.Close()
	decoder := json.NewDecoder(file)
	conf := IRCConfig{}
	err := decoder.Decode(&conf)
	checkErr(err)
	return conf
}

func readDadConfig() DadConfig {
	file, _ := os.Open(dadConfigFile)
	defer file.Close()
	decoder := json.NewDecoder(file)
	conf := DadConfig{}
	err := decoder.Decode(&conf)
	checkErr(err)
	return conf
}

func readMomConfig() MomConfig {
	file, _ := os.Open(momConfigFile)
	defer file.Close()
	decoder := json.NewDecoder(file)
	conf := MomConfig{}
	err := decoder.Decode(&conf)
	checkErr(err)
	return conf
}

// UpdateConfig dispatches a call to the appropriate update function
// based on which bot is being run (mom or dad), parsing the current
// config information and rewriting it to the appropriate config file.
func UpdateConfig() {
	if Dad {
		updateDadConfig()
	} else {
		updateMomConfig()
	}
}

func updateDadConfig() {
	jsonData, err := json.MarshalIndent(Dbot, "", "    ")
	checkErr(err)
	ioutil.WriteFile(dadConfigFile, jsonData, 0644)
}

func updateMomConfig() {
	jsonData, err := json.MarshalIndent(Mbot, "", "    ")
	checkErr(err)
	ioutil.WriteFile(momConfigFile, jsonData, 0644)
}
