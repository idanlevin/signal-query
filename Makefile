build:
	docker build -t signal_query:latest .

run_docker = \
    docker run -ti --rm \
        -v "${HOME}/Library/Application Support/Signal":"/root/.config/Signal" \
        -v ${PWD}/output:/output signal_query:latest \
        --output_file=/output/$(output_file) \
		--output_format="json" \
		--query="SELECT sent_at, ifnull(SUBSTR(sourceUuid, -4, 4),'bdb5') as sender, json_extract(json,'$.quote.id') as reply_to, body as msg FROM messages WHERE conversationId='62b9f987-b634-4f06-84af-e4ab34142841' AND (messages.type='incoming' OR messages.type='outgoing') AND datetime(sent_at / 1000, 'unixepoch', 'localtime') >= datetime('now', '$(query_time_range)', 'localtime') ORDER BY sent_at;"

get_messages:
	$(run_docker)

get24hours: output_file = last24hours.txt
get24hours: query_time_range = -1 day
get24hours: get_messages

getweek: output_file = lastweek.txt
getweek: query_time_range = -7 day
getweek: get_messages

getmonth: output_file = lastmonth.txt
getmonth: query_time_range = -30 day
getmonth: get_messages

getall: output_file = all.txt
getall: query_time_range = -10000 day
getall: get_messages

.PHONY: copydb
copydb:
	./copy_signal_db.sh

it:
	docker run -ti --rm -v ${PWD}/db_copy:/input -v ${PWD}/output:/output signal_query:latest --db_path=/input/db-latest.sqlite --key_file_path=/input/config.json

clean:
	rm -f output/*.txt