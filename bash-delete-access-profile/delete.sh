#!/bin/bash

log_file="execution_log_$(date +%Y%m%d_%H%M%S).log"

echo "Script started at $(date)" >> $log_file

while IFS=, read -r id
do
    echo "[$(date +%Y-%m-%d\ %H:%M:%S)] Deleting access profile with ID: $id" >> $log_file
    response=$(curl -s -w "\nHTTP_STATUS_CODE:%{http_code}\n" --location --request DELETE "https://suzano.api.identitynow.com/v3/access-profiles/$id" \
    --header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnRfaWQiOiJiM2E1ZTAyOC01ZDY0LTRkZjAtOGZkMy05OGY1NmRjNDMwMzQiLCJwb2QiOiJwcmQwMS1ldWNlbnRyYWwxIiwic3Ryb25nX2F1dGhfc3VwcG9ydGVkIjpmYWxzZSwib3JnIjoic3V6YW5vIiwiaWRlbnRpdHlfaWQiOiI1NzRhYjIzZmU5N2E0ODRiYWJjYmZlYjlmNmZkNTZjMSIsInVzZXJfbmFtZSI6InJvZ2VyaW8uc29hcmVzIiwic2NvcGUiOlsiQmc9PSJdLCJzdHJvbmdfYXV0aCI6dHJ1ZSwiZXhwIjoxNzIyOTk4OTI5LCJhdXRob3JpdGllcyI6WyJPUkdfQURNSU4iLCJzcDp1c2VyIl0sImp0aSI6IjI0cTNob29xNWFpY1ZVV2I2cjlaUG81MDNIZyIsImNsaWVudF9pZCI6IjQ5OWFhOWZkODdhMDQwZTA4YzA3ODc5MmYyYjc0MDQ3In0.Y1I0QjA4CHpARfE640YvW1Lk8LhzWeie_dqMNyw6iuE')
    http_status=$(echo "$response" | grep HTTP_STATUS_CODE | cut -d':' -f2)
    echo "[$(date +%Y-%m-%d\ %H:%M:%S)] Response: $response" >> $log_file
    echo "[$(date +%Y-%m-%d\ %H:%M:%S)] HTTP Status Code: $http_status" >> $log_file
    echo "----------------------------------------" >> $log_file
done < $1

echo "Script ended at $(date)" >> $log_file
