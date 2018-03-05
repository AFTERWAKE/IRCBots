package dad

import (
    "testing"
)

func TestAddArticle(t *testing.T) {
    tables := []struct {
        start string
        end string
    }{
        {"baseball", "a baseball"},
        {"astronaut", "an astronaut"},
    }
    for _, table := range tables {
        res := AddArticle(table.start)
        if res != table.end {
            t.Errorf("Incorrect article being added. Got: %s, expected %s", res, table.end)
        }
    }
}

func TestGetChannelTargetOrDefault(t *testing.T) {
    tables := []struct {
        startTo string
        startMsg string
        endTo string
        endMsg string
    }{
        {"#main", "#rents: hello", "#rents", "hello"},
        {"#main", "awest: hello", "awest", "hello"},
        {"#main", "#rents hello", "#main", "#rents hello"},
    }
    for _, table := range tables {
        resTo, resMsg := GetChannelTargetOrDefault(table.startTo, table.startMsg)
        if resTo != table.endTo {
            t.Errorf("Incorrect destination set. Got: %s, expected %s", resTo, table.endTo)
        }
        if resMsg != table.endMsg {
            t.Errorf("Incorrect message set. Got: %s, expected %s", resMsg, table.endMsg)
        }
    }
}

// TODO
func TestGetRandomLeastUsedResponseIndex(t *testing.T) {

}

// TODO
func TestGetICanHazDadJoke(t *testing.T) {
    for i := 0; i < 3; i++ {
        if len(GetICanHazDadJoke()) <= 0 {
            t.Errorf("An error occurred while getting a joke from ICanHazDadJoke.com")
        }
    }
}

// TODO
func TestMessageRateMet(t *testing.T) {

}

// TODO
func TestStringInSlice(t *testing.T) {

}

// TODO
func TestgetSpeakData(t *testing.T) {

}
