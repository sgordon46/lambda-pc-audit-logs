A lambda function with required dependencies to gather audit logs and forward them to SumoLogic with webhook. 

The function will query both Prisma Cloud audit endpoints and Compute Audit endpoints.

The function is built to work with a Cloud Watch event trigger to run every 5 minutes.

The function will also filter out audits from the access token making these calls, as well as any user with "audits" in the username.
