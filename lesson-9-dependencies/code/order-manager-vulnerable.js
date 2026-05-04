// DVSA-ORDER-MANAGER — order-manager.js (VULNERABLE — DO NOT DEPLOY)

const serialize = require('node-serialize');                                     //vulnerable dep
const { LambdaClient, InvokeCommand } = require("@aws-sdk/client-lambda");
const { CognitoIdentityProviderClient, AdminGetUserCommand } = require("@aws-sdk/client-cognito-identity-provider");
const jose = require('node-jose');


exports.handler = (event, context, callback) => {
    var req     = serialize.unserialize(event.body);     
    var headers = serialize.unserialize(event.headers);  
    var auth_header = headers.Authorization || headers.authorization;
    var token_sections = auth_header.split('.');
    var auth_data = jose.util.base64url.decode(token_sections[1]);
    var token = JSON.parse(auth_data);
    var user = token.username;

};
