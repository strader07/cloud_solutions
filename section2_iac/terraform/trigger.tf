resource "aws_cloudwatch_event_rule" "every_one_hour" {
  name                = "every-one-hour"
  description         = "Fires every one hour"
  schedule_expression = "rate(1 hour)"
}

resource "aws_cloudwatch_event_target" "check_foo_every_one_hour" {
  rule      = "${aws_cloudwatch_event_rule.every_one_hour.name}"
  target_id = "lambda-function-write-dynamo"
  arn       = "${aws_lambda_function.lambda-function-write-dynamo.arn}"
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_lambda2" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.lambda-function-write-dynamo.function_name}"
  principal     = "events.amazonaws.com"
  source_arn    = "${aws_cloudwatch_event_rule.every_one_hour.arn}"
}

resource "aws_lambda_event_source_mapping" "dynamo-lambda-trigger" {
    event_source_arn = "${aws_dynamodb_table.iac-apple-prices-dynamo.stream_arn}"
    function_name = "${aws_lambda_function.lambda-function-dynamo-mysql.arn}"
    starting_position = "LATEST"
}