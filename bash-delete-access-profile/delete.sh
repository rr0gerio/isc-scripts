#!/bin/bash

log_file="execution_log_$(date +%Y%m%d_%H%M%S).log"

echo "Script started at $(date)" >> $log_file

while IFS=, read -r id
do
    echo "[$(date +%Y-%m-%d\ %H:%M:%S)] Deleting access profile with ID: $id" >> $log_file
    response=$(curl -s -w "\nHTTP_STATUS_CODE:%{http_code}\n" --location --request DELETE "https://suzano.api.identitynow.com/v3/access-profiles/$id" \
    --header 'Authorization: Bearer ')
    http_status=$(echo "$response" | grep HTTP_STATUS_CODE | cut -d':' -f2)
    echo "[$(date +%Y-%m-%d\ %H:%M:%S)] Response: $response" >> $log_file
    echo "[$(date +%Y-%m-%d\ %H:%M:%S)] HTTP Status Code: $http_status" >> $log_file
    echo "----------------------------------------" >> $log_file
done < $1

echo "Script ended at $(date)" >> $log_file
