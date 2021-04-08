resource "aws_iam_role" "iac-lambda-iam-role" {
  name = "iac-lambda-iam-role"

  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
    {
        "Action": "sts:AssumeRole",
        "Principal": {
        "Service": "lambda.amazonaws.com"
        },
        "Effect": "Allow",
        "Sid": ""
    }
    ]
}
EOF
}

resource "aws_iam_policy" "iac-dynamodb-lambda-policy" {
  name        = "iac-dynamodb-lambda-policy"
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:*"
      ],
      "Resource": ["${aws_dynamodb_table.iac-apple-prices-dynamo.arn}", "${aws_dynamodb_table.iac-apple-prices-dynamo.stream_arn}"]
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "attach-policies" {
  role       = "${aws_iam_role.iac-lambda-iam-role.name}"
  policy_arn = "${aws_iam_policy.iac-dynamodb-lambda-policy.arn}"
}