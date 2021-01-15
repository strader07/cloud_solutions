data "archive_file" "lambda-archive-1" {
  type        = "zip"
  source_file = "lambda/src/dynamo-to-mysql.py"
  output_path = "lambda/packages/lambda1/lambda_function.zip"
}

data "archive_file" "lambda-archive-2" {
  type        = "zip"
  source_file = "lambda/src/write-to-dynamo.py"
  output_path = "lambda/packages/lambda2/lambda_function.zip"
}

resource "aws_lambda_function" "lambda-function-dynamo-mysql" {
  filename         = "lambda/packages/lambda1/lambda_function.zip"
  function_name    = "lambda-function-dynamo-mysql"
  role             = "${aws_iam_role.iac-lambda-iam-role.arn}"
  handler          = "dynamo-to-mysql.handler"
  source_code_hash = "${data.archive_file.lambda-archive-1.output_base64sha256}"
  runtime          = "python3.7"
  timeout          = 300
  memory_size      = 128

  layers = ["${aws_lambda_layer_version.python3-lambda-layer.arn}"]
}

resource "aws_lambda_function" "lambda-function-write-dynamo" {
  filename         = "lambda/packages/lambda2/lambda_function.zip"
  function_name    = "lambda-function-write-dynamo"
  role             = "${aws_iam_role.iac-lambda-iam-role.arn}"
  handler          = "write-to-dynamo.handler"
  source_code_hash = "${data.archive_file.lambda-archive-1.output_base64sha256}"
  runtime          = "python3.7"
  timeout          = 300
  memory_size      = 128

  layers = ["${aws_lambda_layer_version.python3-lambda-layer.arn}"]
}

resource "aws_lambda_layer_version" "python3-lambda-layer" {
  filename         = "lambda/packages/layer/python3-layer.zip"
  layer_name       = "python3-layer"
  source_code_hash = "${filebase64sha256("lambda/packages/layer/python3-layer.zip")}"

  compatible_runtimes = ["python3.6", "python3.7"]
}
