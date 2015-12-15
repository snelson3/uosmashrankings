Will contain steps for converting tio/challonge brackets to rankings,

The uotn file format is how we store tournaments for use by uosmash, it is in
the following format:

{
  "Date": <string>,
  "Matches"{
    {
    "winner": <string>,
    "number": <int>,
    "rnd": <int>,
    "Player2": <string>,
    "Player1": <string>,
    "winners: <bool>"
    }
  },
  "Game": <string>,
  "Entrants": [
    <string>
  ]
}
