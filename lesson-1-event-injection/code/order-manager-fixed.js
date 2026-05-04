// DVSA-ORDER-MANAGER — order-manager.js (PATCHED)
//
// Changes from the vulnerable version:
//   1. Replaced serialize.unserialize(event.body) with JSON.parse(event.body)
//   2. Replaced serialize.unserialize(event.headers) with a safe parser
//      that handles BOTH cases:
//        - event.headers as an object (normal API Gateway case)
//        - event.headers as a string (some test events / internal invocations)

const serialize = require('node-serialize');
const { LambdaClient, InvokeCommand } = require("@aws-sdk/client-lambda");
const { CognitoIdentityProviderClient, AdminGetUserCommand } = require("@aws-sdk/client-cognito-identity-provider");
const jose = require('node-jose');


exports.handler = (event, context, callback) => {
    // Replaced unsafe serialize.unserialize() with safe JSON parsing
    var req     = JSON.parse(event.body);
    var headers = (typeof event.headers === "string") ? JSON.parse(event.headers) : (event.headers || {});

    var auth_header = headers.Authorization || headers.authorization;
    var token_sections = auth_header.split('.');
    var auth_data = jose.util.base64url.decode(token_sections[1]);
    var token = JSON.parse(auth_data);
    var user = token.username;
};
