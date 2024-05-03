--
-- PostgreSQL database dump
--

-- Dumped from database version 16.1
-- Dumped by pg_dump version 16.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: album; Type: TABLE; Schema: public; Owner: sudhip
--

CREATE TABLE public.album (
    id text NOT NULL,
    name text,
    album_type text,
    cover_image_url text
);


ALTER TABLE public.album OWNER TO sudhip;

--
-- Name: albums_by_playcount; Type: VIEW; Schema: public; Owner: sudhip
--

CREATE VIEW public.albums_by_playcount AS
SELECT
    NULL::text AS name,
    NULL::bigint AS play_count,
    NULL::text AS cover_image_url;


ALTER VIEW public.albums_by_playcount OWNER TO sudhip;

--
-- Name: artist; Type: TABLE; Schema: public; Owner: sudhip
--

CREATE TABLE public.artist (
    id text NOT NULL,
    name text
);


ALTER TABLE public.artist OWNER TO sudhip;

--
-- Name: artisttrack; Type: TABLE; Schema: public; Owner: sudhip
--

CREATE TABLE public.artisttrack (
    artist_id text,
    track_id text
);


ALTER TABLE public.artisttrack OWNER TO sudhip;

--
-- Name: scrobble; Type: TABLE; Schema: public; Owner: sudhip
--

CREATE TABLE public.scrobble (
    track_id text,
    played_at timestamp with time zone,
    id integer NOT NULL
);


ALTER TABLE public.scrobble OWNER TO sudhip;

--
-- Name: track; Type: TABLE; Schema: public; Owner: sudhip
--

CREATE TABLE public.track (
    id text NOT NULL,
    name text,
    album_id text,
    explicit boolean,
    popularity bigint,
    duration_ms bigint
);


ALTER TABLE public.track OWNER TO sudhip;

--
-- Name: artists_by_playcount; Type: VIEW; Schema: public; Owner: sudhip
--

CREATE VIEW public.artists_by_playcount AS
 SELECT artist.name,
    count(DISTINCT scrobble.id) AS play_count
   FROM (((public.artist
     JOIN public.artisttrack ON ((artist.id = artisttrack.artist_id)))
     JOIN public.track ON ((track.id = artisttrack.track_id)))
     JOIN public.scrobble ON ((scrobble.track_id = track.id)))
  GROUP BY artist.id, artist.name
  ORDER BY (count(DISTINCT scrobble.id)) DESC;


ALTER VIEW public.artists_by_playcount OWNER TO sudhip;

--
-- Name: scrobble_id_seq; Type: SEQUENCE; Schema: public; Owner: sudhip
--

CREATE SEQUENCE public.scrobble_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.scrobble_id_seq OWNER TO sudhip;

--
-- Name: scrobble_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sudhip
--

ALTER SEQUENCE public.scrobble_id_seq OWNED BY public.scrobble.id;


--
-- Name: scrobbles_by_timestamp; Type: VIEW; Schema: public; Owner: sudhip
--

CREATE VIEW public.scrobbles_by_timestamp AS
 SELECT track.name,
    album.cover_image_url,
    scrobble.played_at
   FROM ((public.track
     JOIN public.scrobble ON ((scrobble.track_id = track.id)))
     JOIN public.album ON ((album.id = track.album_id)))
  ORDER BY scrobble.played_at DESC;


ALTER VIEW public.scrobbles_by_timestamp OWNER TO sudhip;

--
-- Name: spotifyconfig; Type: TABLE; Schema: public; Owner: sudhip
--

CREATE TABLE public.spotifyconfig (
    access_token json,
    name text,
    id integer NOT NULL
);


ALTER TABLE public.spotifyconfig OWNER TO sudhip;

--
-- Name: spotifyconfig_id_seq; Type: SEQUENCE; Schema: public; Owner: sudhip
--

CREATE SEQUENCE public.spotifyconfig_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.spotifyconfig_id_seq OWNER TO sudhip;

--
-- Name: spotifyconfig_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sudhip
--

ALTER SEQUENCE public.spotifyconfig_id_seq OWNED BY public.spotifyconfig.id;


--
-- Name: ten_most_played_albums; Type: VIEW; Schema: public; Owner: sudhip
--

CREATE VIEW public.ten_most_played_albums AS
 SELECT name,
    play_count,
    cover_image_url
   FROM public.albums_by_playcount
 LIMIT 10;


ALTER VIEW public.ten_most_played_albums OWNER TO sudhip;

--
-- Name: ten_most_played_artists; Type: VIEW; Schema: public; Owner: sudhip
--

CREATE VIEW public.ten_most_played_artists AS
 SELECT name,
    play_count
   FROM public.artists_by_playcount
 LIMIT 10;


ALTER VIEW public.ten_most_played_artists OWNER TO sudhip;

--
-- Name: tracks_by_playcount; Type: VIEW; Schema: public; Owner: sudhip
--

CREATE VIEW public.tracks_by_playcount AS
 SELECT track.name,
    count(track.id) AS play_count,
    album.cover_image_url
   FROM ((public.track
     JOIN public.album ON ((track.album_id = album.id)))
     JOIN public.scrobble ON ((scrobble.track_id = track.id)))
  GROUP BY track.name, album.cover_image_url
  ORDER BY (count(track.id)) DESC;


ALTER VIEW public.tracks_by_playcount OWNER TO sudhip;

--
-- Name: ten_most_played_tracks; Type: VIEW; Schema: public; Owner: sudhip
--

CREATE VIEW public.ten_most_played_tracks AS
 SELECT name,
    play_count,
    cover_image_url
   FROM public.tracks_by_playcount
 LIMIT 10;


ALTER VIEW public.ten_most_played_tracks OWNER TO sudhip;

--
-- Name: ten_most_recent_scrobbles; Type: VIEW; Schema: public; Owner: sudhip
--

CREATE VIEW public.ten_most_recent_scrobbles AS
 SELECT name,
    cover_image_url,
    played_at
   FROM public.scrobbles_by_timestamp
 LIMIT 10;


ALTER VIEW public.ten_most_recent_scrobbles OWNER TO sudhip;

--
-- Name: scrobble id; Type: DEFAULT; Schema: public; Owner: sudhip
--

ALTER TABLE ONLY public.scrobble ALTER COLUMN id SET DEFAULT nextval('public.scrobble_id_seq'::regclass);


--
-- Name: spotifyconfig id; Type: DEFAULT; Schema: public; Owner: sudhip
--

ALTER TABLE ONLY public.spotifyconfig ALTER COLUMN id SET DEFAULT nextval('public.spotifyconfig_id_seq'::regclass);


--
-- Name: album idx_16433_sqlite_autoindex_album_1; Type: CONSTRAINT; Schema: public; Owner: sudhip
--

ALTER TABLE ONLY public.album
    ADD CONSTRAINT idx_16433_sqlite_autoindex_album_1 PRIMARY KEY (id);


--
-- Name: artist idx_16438_sqlite_autoindex_artist_1; Type: CONSTRAINT; Schema: public; Owner: sudhip
--

ALTER TABLE ONLY public.artist
    ADD CONSTRAINT idx_16438_sqlite_autoindex_artist_1 PRIMARY KEY (id);


--
-- Name: track idx_16443_sqlite_autoindex_track_1; Type: CONSTRAINT; Schema: public; Owner: sudhip
--

ALTER TABLE ONLY public.track
    ADD CONSTRAINT idx_16443_sqlite_autoindex_track_1 PRIMARY KEY (id);


--
-- Name: scrobble scrobble_pkey; Type: CONSTRAINT; Schema: public; Owner: sudhip
--

ALTER TABLE ONLY public.scrobble
    ADD CONSTRAINT scrobble_pkey PRIMARY KEY (id);


--
-- Name: spotifyconfig spotifyconfig_pkey; Type: CONSTRAINT; Schema: public; Owner: sudhip
--

ALTER TABLE ONLY public.spotifyconfig
    ADD CONSTRAINT spotifyconfig_pkey PRIMARY KEY (id);


--
-- Name: idx_16443_track_album_id; Type: INDEX; Schema: public; Owner: sudhip
--

CREATE INDEX idx_16443_track_album_id ON public.track USING btree (album_id);


--
-- Name: idx_16448_artisttrack_artist_id; Type: INDEX; Schema: public; Owner: sudhip
--

CREATE INDEX idx_16448_artisttrack_artist_id ON public.artisttrack USING btree (artist_id);


--
-- Name: idx_16448_artisttrack_track_id; Type: INDEX; Schema: public; Owner: sudhip
--

CREATE INDEX idx_16448_artisttrack_track_id ON public.artisttrack USING btree (track_id);


--
-- Name: idx_16453_scrobble_track_id; Type: INDEX; Schema: public; Owner: sudhip
--

CREATE INDEX idx_16453_scrobble_track_id ON public.scrobble USING btree (track_id);


--
-- Name: idx_16458_spotifyconfig_name; Type: INDEX; Schema: public; Owner: sudhip
--

CREATE UNIQUE INDEX idx_16458_spotifyconfig_name ON public.spotifyconfig USING btree (name);


--
-- Name: albums_by_playcount _RETURN; Type: RULE; Schema: public; Owner: sudhip
--

CREATE OR REPLACE VIEW public.albums_by_playcount AS
 SELECT album.name,
    count(scrobble.track_id) AS play_count,
    album.cover_image_url
   FROM ((public.album
     JOIN public.track ON ((track.album_id = album.id)))
     JOIN public.scrobble ON ((scrobble.track_id = track.id)))
  GROUP BY album.name, album.id
  ORDER BY (count(scrobble.track_id)) DESC;


--
-- Name: artisttrack artisttrack_artist_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sudhip
--

ALTER TABLE ONLY public.artisttrack
    ADD CONSTRAINT artisttrack_artist_id_fkey FOREIGN KEY (artist_id) REFERENCES public.artist(id);


--
-- Name: artisttrack artisttrack_track_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sudhip
--

ALTER TABLE ONLY public.artisttrack
    ADD CONSTRAINT artisttrack_track_id_fkey FOREIGN KEY (track_id) REFERENCES public.track(id);


--
-- Name: scrobble scrobble_track_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sudhip
--

ALTER TABLE ONLY public.scrobble
    ADD CONSTRAINT scrobble_track_id_fkey FOREIGN KEY (track_id) REFERENCES public.track(id);


--
-- Name: track track_album_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sudhip
--

ALTER TABLE ONLY public.track
    ADD CONSTRAINT track_album_id_fkey FOREIGN KEY (album_id) REFERENCES public.album(id);


--
-- PostgreSQL database dump complete
--

