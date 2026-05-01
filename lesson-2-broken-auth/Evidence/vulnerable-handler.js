// ❌ Vulnerable Code

exports.handler = async (event) => {
    const token = event.headers.Authorization;

    const payload = JSON.parse(
        Buffer.from(token.split('.')[1], 'base64').toString()
    );

    const username = payload.username;

    return {
        statusCode: 200,
        body: JSON.stringify({ message: "User: " + username })
    };
};
