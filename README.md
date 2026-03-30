# Pomodoro

App name: Pure Focus

To-do
- [ ] Building MVP
- [ ] Producthunt Upload

# Desired Outcome

Home
- Focus Calendar: Visualize how much focus session has been completed. Benchmark green squares(contribution graph) of github
- Graph of todo and nottodo list: Visualize how much todo and nottodo list has been completed.
- Collection: User can view their achievements. Gallery of photos and typography of quotes that the user has completed.

Set new cycle
- Selection: User choose the photos and quotes set. User can also builde their own set by choosing photos and quotes they want. They can use the collection of photos and quotes.
- Setting: User choose the time of focus and break sessions. They can also make a cycle by drag and drop.
- Todo and nottodo: User can make list of todo and nottodo for each focus session. During the session user can check the todo list and nottodo list. If the focus session is completed, checked todo list will be accumulated and unchecked nottodo list will be accumulated. User can browse it on the home page.
- Backlog (Memo): User can write a memo for each session. This can be used for what they will focus on during the session or what they should avoid during the session.
- Backlog (Replacing the quote): Agent can keep making words base on the goal, todo, nottodo, and memo.

Timer
- Backgound is consist of photos and quotes. Photos that user wants and motivational quotes.
  - Photo have source and quote have author.
- Pomodoro technique
  - Focus session:  Default 25 minutes (for testing, set to 25 seconds)
  - Break session:  Default 5 minutes and long break time is 15 minutes (for testing, set to 5 seconds and 15 seconds)
  - Pomodoro(cycle): Sets of focus sessions and break sessions are called cycle. Default is 4 Focus sessions and 3 Break sessions.
  - Start
  - Stop: If the user clicks anywhere 3 times everything will be reset.
- Progress visualization: Progress bar showing how much time is left
- Timer display: Show the timer counting down in real-time. This makes the user feel time is going
- Backlog (tracker): User can track how agent is working.

Reward
After 4 focus sessions are completed user can get a reward. It should be choosen on the same page with pop-up.
- Sets of photos and quotes that the user completed.
- User can add their own quote or photo.
  - User quote: Making my own quote and this can be share with others. User can choose public or private.
  - User photo: Uploading users own photo and it can be shared with others. User can choose public or private.
    - Search: Search and select from Unsplash. Follow the Unsplash guideline to write the source of the photo.
    - Upload: Source becomes the user
    - Public/Private 

Admin
- Account: People can easily sign up with google, apple, facebook, linkedin.
- User setting: Nickname, Profile photo(Default is alphabet of nickname)

Design
Concept: Minimalistic design for lower distraction. Photos on the background with typography of the quotes
Responsive Design: It should be used on iphone(mobile), ipad(tablet), mac(desktop).


Architecture
Clear architecture how does the application works.

# Stitch Prototype
https://stitch.withgoogle.com/projects/8374986689812423367

Integration document:
- [docs/pure_focus_stitch_integration.md](docs/pure_focus_stitch_integration.md)


Business Model
- Ads

