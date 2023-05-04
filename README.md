# Signal Query

This project provides a Python script to query Signal's encrypted SQLite databases using SQLCipher encryption. It supports both single-query mode and interactive mode, with the option to save query results to an output file.

## Requirements
For running locally you'll need:
- Python 3.6+
- pysqlcipher3
- libsqlcipher

For running via Docker you'll need to install **Docker Engine**.

## Installation

### Local Installation

1. Install `libsqlcipher`:

   For Debian/Ubuntu-based systems:

   ```
   sudo apt-get install libsqlcipher-dev
   ```

   For macOS with Homebrew:

   ```
   brew install sqlcipher
   ```

2. Install the required Python packages:

   ```
   pip install pysqlcipher3
   ```

### Docker Installation

1. Build the Docker image:

   ```
   docker build -t signal_query .
   ```

## Usage

```
usage: main.py [-h] [--query QUERY] [--db_path DB_PATH] [--key_file_path KEY_FILE_PATH] [--output_file OUTPUT_FILE]

Execute SQL query on an encrypted SQLite database.

optional arguments:
  -h, --help            show this help message and exit
  --query QUERY         SQL query to execute (optional)
  --db_path DB_PATH     Path to the encrypted SQLite database (default: Signal's db.sqlite based on the OS)
  --key_file_path KEY_FILE_PATH
                        Path to the key file (default: Signal's config.json file based on the OS)
  --output_file OUTPUT_FILE
                        Path to the output file (optional)
```

> **NOTE**: Signal's default storage path is `${HOME}/Library/Application Support/Signal` on MacOS and Linux and `%USERPROFILE%\AppData\Roaming\Signal` on Windows.

### Local Usage

- To run a single query and get the result to stdout:

   ```
   python main.py --query="SELECT * FROM messages limit 5;"
   ```

- To use the script in interactive query mode, simply omit the `--query` argument:

   ```
   python main.py
   ```

- To provide a db file and key path and save the query results into a file:

   ```
   python main.py --db_path=path/to/your/database.db --key_file_path=path/to/your/keyfile.txt --output_file=path/to/your/outputfile.txt
   ```

### Docker Usage
> **Note**: By default the script will look in `/root/.config/` for the Signal database and key file, so by mounting the volume to this location you won't need to supply db and key paths. 

- To run a single query and get the result to stdout (from MacOS/Linux):
    ```
    docker run -ti --rm -v "${HOME}/Library/Application Support/Signal":"/root/.config/Signal" signal_query:latest --query="SELECT * FROM messages limit 5;"

    ```
- To use the script in interactive query mode, simply omit the `--query` argument (from MacOS/Linux):

   ```
   docker run -ti --rm -v "${HOME}/Library/Application Support/Signal":"/root/.config/Signal" signal_query:latest
   ```

- To provide a db file and key path and save the query results into a file (from MacOS/Linux):

   ```
      docker run -ti --rm -v "${HOME}/Library/Application Support/Signal":"/root/.config/Signal" signal_query:latest --db_path=data/your_database.db --key_file_path=data/your_keyfile.txt
   ```

## Signal Database Schema

### Messages Table

The `messages` table in the Signal database stores the messages exchanged between users. The following table lists the columns of the `messages` table and provides a brief explanation for each column:

| Column Name                | Description                                               |
|----------------------------|-----------------------------------------------------------|
| body                       | Content of the message                                    |
| conversationId             | Identifier for the conversation thread                    |
| expires_at                 | Time when the message expires                             |
| expireTimer                | Duration of the message timer                             |
| expirationStartTimestamp   | Timestamp when the expiration timer started               |
| hasAttachments             | Whether the message has attachments                       |
| hasFileAttachments         | Whether the message has file attachments                  |
| hasVisualMediaAttachments  | Whether the message has visual media attachments          |
| id                         | Unique identifier for the message                         |
| isChangeCreatedByUs        | Whether the change was created by us                      |
| isErased                   | Whether the message is erased                             |
| isViewOnce                 | Whether the message is view-once                          |
| json                       | JSON representation of the message                        |
| messageTimer               | Duration of the message timer                             |
| messageTimerExpiresAt      | Time when the message timer expires                       |
| messageTimerStart          | Timestamp when the message timer started                  |
| received_at                | Timestamp when the message was received                   |
| readStatus                 | Read status of the message                                |
| rowid                      | Row ID in the SQLite table                                |
| schemaVersion              | Schema version of the message                             |
| seenStatus                 | Seen status of the message                                |
| sent_at                    | Timestamp when the message was sent                       |
| serverGuid                 | GUID of the message on the server                         |
| source                     | Address (phone number) of the sender/recipient            |
| sourceDevice               | Device ID of the sender                                   |
| sourceUuid                 | UUID of the sender/recipient                              |
| storyDistributionListId    | Identifier of the story distribution list                 |
| storyId                    | Identifier of the story                                   |
| type                       | Type of the message (incoming, outgoing, etc.)            |

## Signal Message Types

The `messages` table in the Signal database includes a `type` column that describes the nature of each message. The following table lists the different message types and provides a brief explanation for each type:

| Message Type              | Description                                              |
|---------------------------|----------------------------------------------------------|
| incoming                  | Incoming message from another user                       |
| outgoing                  | Outgoing message sent by the user                        |
| group-v2-change           | Group update message for a group (e.g., member added)    |
| keychange                 | Message related to key changes                           |
| profile-change            | Message related to profile changes                       |
| timer-notification        | Message related to disappearing message timer changes    |
| change-number-notification| Message related to a user's phone number change          |
| call-history              | Message related to call history (e.g., missed call)      |

## Conversations Table
The `conversations` table in the Signal database stores information about individual contacts, groups, and other person threads. While the name "conversations" might be confusing, this table is essentially a collection of user profiles and group information. The following table lists the columns of the `conversations` table and provides a brief explanation for each column:

| Column Name          | Description                                               |
|----------------------|-----------------------------------------------------------|
| active_at            | Timestamp when the contact was last active                |
| e164                 | E.164 formatted phone number of the contact               |
| groupId              | Group identifier if the contact is a group                |
| id                   | Unique identifier for the contact                         |
| json                 | JSON representation of the contact                        |
| members              | List of member UUIDs in the contact (for groups)          |
| name                 | Name of the contact or group                              |
| profileFamilyName    | Family name of the contact (from Signal profile)          |
| profileFullName      | Full name of the contact (from Signal profile)            |
| profileLastFetchedAt | Timestamp when the contact's profile was last fetched     |
| profileName          | First name of the contact (from Signal profile)           |
| type                 | Type of the contact (private or group)                    |
| uuid                 | UUID of the contact                                       |


### Correlation
The right way to correlate between the messages and the conversations (contacts) is to us the `uuid` field from `conversations` and `sourceUuid` from `messages` table, for example:

```sql
select sent_at, profileFullname, body from messages 
    inner join conversations on messages.sourceUuid = conversations.uuid 
    where messages.type="incoming" or messages.type="outgoing" 
    order by sent_at 
    limit 100;
```