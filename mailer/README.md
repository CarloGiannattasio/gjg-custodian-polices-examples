# Cloud Custodian Mailer (shared)

All repo policies use **`notify`** to send **Slack** and **email** via this mailer. Custodian enqueues to SQS; **c7n-mailer** delivers to `slack://#cloud-custodian-alerts`, `cloud-custodian@example.com`, and `resource-owner` (from resource tags).

1. Copy `mailer.example.yml` to `mailer.yml` and fill in your queue, addresses, and Slack webhook.
2. Deploy the mailer Lambda: `c7n-mailer --config mailer/mailer.yml -t sqs --update-lambda`
3. In each policy file, set the `notify` transport `queue` URL to match `queue_url` here.

Do not commit real webhooks or production queue URLs if this repository is public; use `mailer.yml` locally or in CI secrets.
