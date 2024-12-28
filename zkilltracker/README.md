ZKillTracker

Todo:
Admin view
- Refresh data button that refreshes kills&memberKills for current and past month.
- Add data via a popup and nice selectors:
1. member using <characterID, characterName, corporationID>. Should return success
2. Corporation+months <corporationID> hits off input for corporation+months, should return success
- File upload for alliance months after Shieks transposer

Member view
- Corp selector, member selector
- Line graph of progress over time (kills per month)
- Card of total kills in Sigma
- Table detailing kills per month
- Progress this month

Corporation view
- List people who have had kills and how many

Backend
- Add member route
- Add corporation route
- Threadsafe sqlite (sqlalchemy?)
- Kick off repopulate job in diff thread (kills & memberKills) (celery?)
- Execute corporation, add refresh in same thread
- Fill characterID, characterName, corporationID table
- Mains-alts matching? iff => Kaka
- Authentication on admin calls

Frontend
- Next.js
- Typescript
- API calls on server files?
- Tab switch and login handling via Contextmanager

Mantine goodies
- Table
- Card/Paper
- LoadingOverlay | Alert/notification
- Modal with form? Or textInput/numberinput -> Contentmodals | updatingContext modal
- Tooltips?
- NumberFormatter in Table
- Appshell
- Dropzone?