resource "aws_dynamodb_table" "iac-apple-prices-dynamo" {
  name = "iac-apple-prices-dynamo"
  read_capacity = 5
  write_capacity = 5
  hash_key = "ID"
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  attribute {
        name = "ID"
        type = "S"
    }
}