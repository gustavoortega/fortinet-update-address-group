## Steps to deploy

1. Crear pub/sub
`gcloud pubsub topics create address-deploybot`

2. Crear scheduler
`gcloud scheduler jobs create pubsub address-deploybot --schedule="0 * * * *" --topic=address-deploybot  --message-body='{"key":"value"}' --location=us-central1`

3. Deployar
`sls deploy`