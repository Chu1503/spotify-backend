// index.js
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
    origin: "https://spotify-frontend-sigma.vercel.app",
    credentials: true,
  })
);
app.use(express.json());
app.use(cookieParser());

// Environment Variables
const CLIENT_ID = process.env.CLIENT_ID;
const CLIENT_SECRET = process.env.CLIENT_SECRET;
const REDIRECT_URI = process.env.REDIRECT_URI;

// Spotify Scopes
const scope =
  "user-read-private user-read-email playlist-read-private user-read-recently-played user-top-read playlist-modify-public playlist-modify-private playlist-read-collaborative";

// Store refresh tokens associated with users
const userTokens = {};

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

  res.redirect(`https://accounts.spotify.com/authorize?${authQueryParameters}`);
});

// Route: /callback
app.get("/callback", async (req, res) => {
  const code = req.query.code || null;
  const state = req.query.state || null;
  const storedState = req.cookies ? req.cookies["spotify_auth_state"] : null;

  if (state === null || state !== storedState) {
    return res.redirect(
      "/#" + querystring.stringify({ error: "state_mismatch" })
    );
  }

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
    const response = await axios(authOptions);
    const access_token = response.data.access_token;
    const refresh_token = response.data.refresh_token;

    // Store refresh_token for this user session
    userTokens[req.sessionID] = refresh_token;

    res.redirect(`https://spotify-frontend-sigma.vercel.app/`);
  } catch (error) {
    console.error(
      "Error retrieving access token:",
      error.response ? error.response.data : error.message
    );
    res.redirect("/#" + querystring.stringify({ error: "invalid_token" }));
  }
});

// Helper Function: Refresh Access Token
async function getAccessToken(req) {
  const refresh_token = userTokens[req.sessionID];
  if (!refresh_token) throw new Error("No refresh token available.");

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

  const response = await axios(authOptions);
  return response.data.access_token;
}

// Route: Fetch User Profile
app.get("/api/me", async (req, res) => {
  try {
    const accessToken = await getAccessToken(req);
    const response = await axios.get("https://api.spotify.com/v1/me", {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    res.json(response.data);
  } catch (error) {
    console.error("Error fetching user profile:", error);
    res
      .status(400)
      .send(
        error.response
          ? error.response.data
          : { error: "failed_to_fetch_profile" }
      );
  }
});

// Route: Fetch User Playlists
app.get("/api/me/playlists", async (req, res) => {
  try {
    const accessToken = await getAccessToken(req);
    const response = await axios.get(
      "https://api.spotify.com/v1/me/playlists",
      {
        headers: { Authorization: `Bearer ${accessToken}` },
      }
    );
    res.json(response.data);
  } catch (error) {
    console.error("Error fetching user playlists:", error);
    res
      .status(400)
      .send(
        error.response
          ? error.response.data
          : { error: "failed_to_fetch_playlists" }
      );
  }
});

// Start the Server
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
