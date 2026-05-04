// DVSA-ORDER-MANAGER — order-manager.js 
// Changes from the vulnerable version:
//   1. Removed:  const serialize = require('node-serialize');
//   2. Replaced serialize.unserialize() with native JSON.parse() on
//      both event.body and event.headers.
//   3. Run `npm uninstall node-serialize` to drop the dependency.

const { LambdaClient, InvokeCommand } = require("@aws-sdk/client-lambda");
const { CognitoIdentityProviderClient, AdminGetUserCommand } = require("@aws-sdk/client-cognito-identity-provider");
const jose = require('node-jose');


exports.handler = (event, context, callback) => {
    // Replaced serialize.unserialize() with safe JSON.parse()
    var req     = JSON.parse(event.body);
    var headers = JSON.parse(event.headers);

    var auth_header = headers.Authorization || headers.authorization;
    var token_sections = auth_header.split('.');
    var auth_data = jose.util.base64url.decode(token_sections[1]);
    var token = JSON.parse(auth_data);
    var user = token.username;

};
