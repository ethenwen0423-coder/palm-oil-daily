on run argv
	if (count of argv) is not 2 then error "recipient and message are required"
	set recipientHandle to item 1 of argv
	set messageText to item 2 of argv

	tell application "Messages"
		set usableServices to every service whose service type is iMessage
		if (count of usableServices) is 0 then error "no iMessage service is configured"
		set targetService to item 1 of usableServices
		set targetBuddy to buddy recipientHandle of targetService
		send messageText to targetBuddy
	end tell
end run
