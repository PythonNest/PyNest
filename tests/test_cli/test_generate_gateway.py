from nest.cli.src.generate.generate_service import GenerateService


def test_generate_gateway_creates_gateway_file(tmp_path):
    GenerateService().generate_gateway("chat", str(tmp_path))

    gateway_file = tmp_path / "chat_gateway.py"

    assert gateway_file.exists()
    assert (
        "from nest.websockets import MessageBody, SubscribeMessage, WebSocketGateway"
        in gateway_file.read_text()
    )
    assert '@WebSocketGateway(namespace="/chat")' in gateway_file.read_text()
    assert '@SubscribeMessage("ping")' in gateway_file.read_text()
