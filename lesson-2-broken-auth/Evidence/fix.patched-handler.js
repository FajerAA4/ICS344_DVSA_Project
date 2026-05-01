

const verifyCognitoJwt = require('./verify'); // assumed helper

exports.handler = async (event) => {
    try {
        const auth = event.headers.Authorization || "";
        const token = auth.replace("Bearer ", "");

        const verified = await verifyCognitoJwt(token);

        const username = verified.username;

        return {
            statusCode: 200,
            body: JSON.stringify({ message: "User: " + username })
        };

    } catch (err) {
        return {
            statusCode: 401,
            body: JSON.stringify({
                status: "err",
                msg: "Invalid token"
            })
        };
    }
};
