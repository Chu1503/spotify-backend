const express = require("express");
const axios = require("axios");
const cors = require("cors");
const querystring = require("querystring");
const dotenv = require("dotenv");
const cookieParser = require("cookie-parser");

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(
  cors({
    origin: "https://spotify-frontend-sigma.vercel.app", // Replace with your frontend URL
    credentials: true,
  })
);
app.use(express.json());
app.use(cookieParser());

// Environment Variables
const CLIENT_ID = process.env.CLIENT_ID;
const CLIENT_SECRET = process.env.CLIENT_SECRET;
const REDIRECT_URI = process.env.REDIRECT_URI;

// Utility Function to Generate Random String
const generateRandomString = (length) => {
  let text = "";
  const possible =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  for (let i = 0; i < length; i++) {
    text += possible.charAt(Math.floor(Math.random() * possible.length));
  }
  return text;
};

// Spotify Scopes
const scope =
  "user-read-private user-read-email playlist-read-private user-read-recently-played user-top-read playlist-modify-public playlist-modify-private playlist-read-collaborative";

// Route: /login
app.get("/login", (req, res) => {
  const state = generateRandomString(16);

  // Set state in an HTTP-only, secure cookie
  res.cookie("spotify_auth_state", state, {
    httpOnly: true,
    secure: true,
    sameSite: "lax",
  });

  const authQueryParameters = querystring.stringify({
    response_type: "code",
    client_id: CLIENT_ID,
    scope: scope,
    redirect_uri: REDIRECT_URI,
    state: state,
  });

  console.log("Redirecting to Spotify for authorization with state:", state);
  res.redirect(`https://accounts.spotify.com/authorize?${authQueryParameters}`);
});

// Route: /callback
app.get("/callback", async (req, res) => {
  const code = req.query.code || null;
  const state = req.query.state || null;
  const storedState = req.cookies ? req.cookies["spotify_auth_state"] : null;

  if (state === null || state !== storedState) {
    console.log("State mismatch error during callback.");
    return res.redirect(
      "/#" + querystring.stringify({ error: "state_mismatch" })
    );
  }

  // Clear the state cookie
  res.clearCookie("spotify_auth_state");

  const authOptions = {
    method: "post",
    url: "https://accounts.spotify.com/api/token",
    data: querystring.stringify({
      code: code,
      redirect_uri: REDIRECT_URI,
      grant_type: "authorization_code",
    }),
    headers: {
      "content-type": "application/x-www-form-urlencoded",
      Authorization:
        "Basic " +
        Buffer.from(CLIENT_ID + ":" + CLIENT_SECRET).toString("base64"),
    },
  };

  try {
    console.log("Requesting access token with authorization code:", code);
    const response = await axios(authOptions);
    const access_token = response.data.access_token;
    const refresh_token = response.data.refresh_token;
    console.log("Received access token and refresh token from Spotify.");

    // Redirect to frontend with tokens in the hash
    res.redirect(
      `https://spotify-frontend-sigma.vercel.app/#${querystring.stringify({
        access_token: access_token,
        refresh_token: refresh_token,
      })}`
    );
  } catch (error) {
    console.error(
      "Error retrieving access token:",
      error.response ? error.response.data : error.message
    );
    res.redirect("/#" + querystring.stringify({ error: "invalid_token" }));
  }
});

// Route: /refresh_token
app.get("/refresh_token", async (req, res) => {
  const refresh_token = req.query.refresh_token;
  console.log("Received request to refresh token:", refresh_token);

  if (!refresh_token) {
    return res.status(400).send({ error: "refresh_token_missing" });
  }

  const authOptions = {
    method: "post",
    url: "https://accounts.spotify.com/api/token",
    data: querystring.stringify({
      grant_type: "refresh_token",
      refresh_token: refresh_token,
    }),
    headers: {
      "content-type": "application/x-www-form-urlencoded",
      Authorization:
        "Basic " +
        Buffer.from(CLIENT_ID + ":" + CLIENT_SECRET).toString("base64"),
    },
  };

  try {
    const response = await axios(authOptions);
    console.log("Refreshed access token successfully.");
    res.send({ access_token: response.data.access_token });
  } catch (error) {
    console.error(
      "Error refreshing access token:",
      error.response ? error.response.data : error.message
    );
    res
      .status(400)
      .send(
        error.response ? error.response.data : { error: "token_refresh_failed" }
      );
  }
});

// Start the Server
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
