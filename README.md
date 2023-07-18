
# Amazon Transcribe Streaming in Python with Websockets

This example project demonstrates how to use Amazon Transcribe in real-time with Python and Websockets. It contains no dependencies on [Boto3](https://aws.amazon.com/sdk-for-python/).

# Requirements

- Python 3.10
- websockets (`pip install websockets`)
- AWS credentials

# How to Use

The example file is named `example.py`. It will send audio in 100ms 'chunks' per payload, serialized/marshalled into the [AWS EventStream `AudioEvent` format](https://docs.aws.amazon.com/transcribe/latest/dg/streaming-setting-up.html). The file that gets streamed is `example_call_2_channel.wav`. The JSON response from Amazon Transcribe is parsed and the partial result transcripts are printed to the terminal.

Before running the example, make sure that you have your AWS `AWS_ACCESS_KEY_ID`,  `AWS_SECRET_ACCESS_KEY`, and `AWS_DEFAULT_REGION` (region is optional, and will default to `us-east-1`). You can fill them into the variables defined in `example.py`, or set environment variables with the same names.  Please note: If you are using temporary credentials, for example, from STS, you will also need to set the `AWS_SESSION_TOKEN`. 

If you are swapping out the audio file for something else, please configure at the `# Sound settings` variables and update the media_encoding, number_of_channels, 

To run the example, navigate via the cli to the folder, and type `python3 example.py`

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

