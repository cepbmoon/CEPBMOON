--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.10
-- Dumped by pg_dump version 9.6.10

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: _sqlite_sequence; Type: TABLE; Schema: public; Owner: rebasedata
--

CREATE TABLE public._sqlite_sequence (
    name character varying(16) DEFAULT NULL::character varying,
    seq smallint
);


ALTER TABLE public._sqlite_sequence OWNER TO rebasedata;

--
-- Name: _tabcursoseccion; Type: TABLE; Schema: public; Owner: rebasedata
--

CREATE TABLE public._tabcursoseccion (
    "idCursoSeccion" smallint,
    "nomCursoSeccion" character varying(11) DEFAULT NULL::character varying,
    "abrCursoSeccion" character varying(4) DEFAULT NULL::character varying
);


ALTER TABLE public._tabcursoseccion OWNER TO rebasedata;

--
-- Name: _tabdelegaciones; Type: TABLE; Schema: public; Owner: rebasedata
--

CREATE TABLE public._tabdelegaciones (
    "idSesion" smallint,
    "idDelegacion" smallint,
    "nomDelegacion" character varying(28) DEFAULT NULL::character varying,
    "idTipoDelegacion" smallint,
    bandera character varying(4) DEFAULT NULL::character varying,
    turnos smallint
);


ALTER TABLE public._tabdelegaciones OWNER TO rebasedata;

--
-- Name: _tabdelegados; Type: TABLE; Schema: public; Owner: rebasedata
--

CREATE TABLE public._tabdelegados (
    "idDelegado" character varying(1) DEFAULT NULL::character varying,
    "nomDelegado" character varying(1) DEFAULT NULL::character varying,
    "idDelegacion" character varying(1) DEFAULT NULL::character varying,
    "alumnoCEPB" character varying(1) DEFAULT NULL::character varying,
    "idCursoSeccion" character varying(1) DEFAULT NULL::character varying
);


ALTER TABLE public._tabdelegados OWNER TO rebasedata;

--
-- Name: _tabmesa; Type: TABLE; Schema: public; Owner: rebasedata
--

CREATE TABLE public._tabmesa (
    "idSesion" character varying(1) DEFAULT NULL::character varying,
    "Presidente" character varying(1) DEFAULT NULL::character varying,
    "Moderador" character varying(1) DEFAULT NULL::character varying,
    "Secretario" character varying(1) DEFAULT NULL::character varying,
    "Evaluador" character varying(1) DEFAULT NULL::character varying,
    "Foro" character varying(1) DEFAULT NULL::character varying,
    "Año" character varying(1) DEFAULT NULL::character varying
);


ALTER TABLE public._tabmesa OWNER TO rebasedata;

--
-- Name: _tabobservaciones; Type: TABLE; Schema: public; Owner: rebasedata
--

CREATE TABLE public._tabobservaciones (
    "idSesion" character varying(1) DEFAULT NULL::character varying,
    "idObs" character varying(1) DEFAULT NULL::character varying,
    "descObs" character varying(1) DEFAULT NULL::character varying,
    "puntajeObs" character varying(1) DEFAULT NULL::character varying
);


ALTER TABLE public._tabobservaciones OWNER TO rebasedata;

--
-- Name: _tabpuntaje; Type: TABLE; Schema: public; Owner: rebasedata
--

CREATE TABLE public._tabpuntaje (
    "idSesion" character varying(1) DEFAULT NULL::character varying,
    "idPuntaje" character varying(1) DEFAULT NULL::character varying,
    "idDelegado" character varying(1) DEFAULT NULL::character varying,
    "idObs" character varying(1) DEFAULT NULL::character varying,
    "descObs" character varying(1) DEFAULT NULL::character varying,
    puntaje character varying(1) DEFAULT NULL::character varying
);


ALTER TABLE public._tabpuntaje OWNER TO rebasedata;

--
-- Name: _tabsesion; Type: TABLE; Schema: public; Owner: rebasedata
--

CREATE TABLE public._tabsesion (
    "idSesion" character varying(1) DEFAULT NULL::character varying,
    "nomForo" character varying(1) DEFAULT NULL::character varying
);


ALTER TABLE public._tabsesion OWNER TO rebasedata;

--
-- Name: _tabtiempos; Type: TABLE; Schema: public; Owner: rebasedata
--

CREATE TABLE public._tabtiempos (
    "idSesion" character varying(1) DEFAULT NULL::character varying,
    leer smallint,
    cuestionar smallint,
    pensar smallint,
    contestar smallint
);


ALTER TABLE public._tabtiempos OWNER TO rebasedata;

--
-- Name: _tabtipodelegacion; Type: TABLE; Schema: public; Owner: rebasedata
--

CREATE TABLE public._tabtipodelegacion (
    "idTipoDelegacion" smallint,
    "nomTipoDelegacion" character varying(12) DEFAULT NULL::character varying
);


ALTER TABLE public._tabtipodelegacion OWNER TO rebasedata;

--
-- Data for Name: _sqlite_sequence; Type: TABLE DATA; Schema: public; Owner: rebasedata
--

COPY public._sqlite_sequence (name, seq) FROM stdin;
tabCursoSeccion	0
tabDelegados	0
tabSesion	0
tabObservaciones	0
tabPuntaje	0
\.


--
-- Data for Name: _tabcursoseccion; Type: TABLE DATA; Schema: public; Owner: rebasedata
--

COPY public._tabcursoseccion ("idCursoSeccion", "nomCursoSeccion", "abrCursoSeccion") FROM stdin;
1	SÉPTIMO "A"	7° A
2	SÉPTIMO "B"	7° B
3	OCTAVO "A"	8° A
4	OCTAVO "B"	8° B
5	NOVENO "A"	9° A
6	NOVENO "B"	9° B
7	PRIMERO "A"	1° A
8	PRIMERO "B"	1° B
9	PRIMERO "T"	1° T
10	SEGUNDO "A"	2° A
11	SEGUNDO "B"	2° B
12	SEGUNDO "T"	2° T
13	TERCERO "A"	3° A
14	TERCERO "B"	3° B
15	TERCERO "T"	3° T
\.


--
-- Data for Name: _tabdelegaciones; Type: TABLE DATA; Schema: public; Owner: rebasedata
--

COPY public._tabdelegaciones ("idSesion", "idDelegacion", "nomDelegacion", "idTipoDelegacion", bandera, turnos) FROM stdin;
0	1	Afganistán	1	link	0
0	2	Albania	1	link	0
0	3	Alemania	1	link	0
0	4	Andorra	1	link	0
0	5	Angola	1	link	0
0	6	Antigua y Barbuda	1	link	0
0	7	Arabia Saudita	1	link	0
0	8	Argelia	1	link	0
0	9	Argentina	1	link	0
0	10	Armenia	1	link	0
0	11	Australia	1	link	0
0	12	Austria	1	link	0
0	13	Azerbaiyán	1	link	0
0	14	Bahamas	1	link	0
0	15	Baréin	1	link	0
0	16	Bangladés	1	link	0
0	17	Barbados	1	link	0
0	18	Belarús	1	link	0
0	19	Bélgica	1	link	0
0	20	Belice	1	link	0
0	21	Benín	1	link	0
0	22	Bután	1	link	0
0	23	Bolivia	1	link	0
0	24	Bosnia y Herzegovina	1	link	0
0	25	Botsuana	1	link	0
0	26	Brasil	1	link	0
0	27	Brunéi	1	link	0
0	28	Bulgaria	1	link	0
0	29	Burkina Faso	1	link	0
0	30	Burundi	1	link	0
0	31	Cabo Verde	1	link	0
0	32	Camboya	1	link	0
0	33	Camerún	1	link	0
0	34	Canadá	1	link	0
0	35	Catar	1	link	0
0	36	Chad	1	link	0
0	37	Chile	1	link	0
0	38	China	1	link	0
0	39	Chipre	1	link	0
0	40	Colombia	1	link	0
0	41	Comoras	1	link	0
0	42	Corea del Norte	1	link	0
0	43	Corea del Sur	1	link	0
0	44	Costa Rica	1	link	0
0	45	Costa de Marfil	1	link	0
0	46	Croacia	1	link	0
0	47	Cuba	1	link	0
0	48	Dinamarca	1	link	0
0	49	Dominica	1	link	0
0	50	Ecuador	1	link	0
0	51	Egipto	1	link	0
0	52	El Salvador	1	link	0
0	53	Emiratos Árabes Unidos	1	link	0
0	54	Eritrea	1	link	0
0	55	Eslovaquia	1	link	0
0	56	Eslovenia	1	link	0
0	57	España	1	link	0
0	58	Estados Unidos	1	link	0
0	59	Estonia	1	link	0
0	60	Esuatini	1	link	0
0	61	Etiopía	1	link	0
0	62	Filipinas	1	link	0
0	63	Finlandia	1	link	0
0	64	Fiyi	1	link	0
0	65	Francia	1	link	0
0	66	Gabón	1	link	0
0	67	Gambia	1	link	0
0	68	Georgia	1	link	0
0	69	Ghana	1	link	0
0	70	Granada	1	link	0
0	71	Grecia	1	link	0
0	72	Guatemala	1	link	0
0	73	Guinea	1	link	0
0	74	Guinea-Bisáu	1	link	0
0	75	Guinea Ecuatorial	1	link	0
0	76	Guyana	1	link	0
0	77	Haití	1	link	0
0	78	Honduras	1	link	0
0	79	Hungría	1	link	0
0	80	India	1	link	0
0	81	Indonesia	1	link	0
0	82	Irak	1	link	0
0	83	Irán	1	link	0
0	84	Irlanda	1	link	0
0	85	Islandia	1	link	0
0	86	Islas Marshall	1	link	0
0	87	Islas Salomón	1	link	0
0	88	Israel	1	link	0
0	89	Italia	1	link	0
0	90	Jamaica	1	link	0
0	91	Japón	1	link	0
0	92	Jordania	1	link	0
0	93	Kazajistán	1	link	0
0	94	Kenia	1	link	0
0	95	Kirguistán	1	link	0
0	96	Kiribati	1	link	0
0	97	Kuwait	1	link	0
0	98	Laos	1	link	0
0	99	Lesoto	1	link	0
0	100	Letonia	1	link	0
0	101	Líbano	1	link	0
0	102	Liberia	1	link	0
0	103	Libia	1	link	0
0	104	Liechtenstein	1	link	0
0	105	Lituania	1	link	0
0	106	Luxemburgo	1	link	0
0	107	Madagascar	1	link	0
0	108	Malasia	1	link	0
0	109	Malaui	1	link	0
0	110	Maldivas	1	link	0
0	111	Malí	1	link	0
0	112	Malta	1	link	0
0	113	Marruecos	1	link	0
0	114	Mauricio	1	link	0
0	115	Mauritania	1	link	0
0	116	México	1	link	0
0	117	Micronesia	1	link	0
0	118	Moldavia	1	link	0
0	119	Mónaco	1	link	0
0	120	Mongolia	1	link	0
0	121	Montenegro	1	link	0
0	122	Mozambique	1	link	0
0	123	Myanmar	1	link	0
0	124	Namibia	1	link	0
0	125	Nauru	1	link	0
0	126	Nepal	1	link	0
0	127	Nicaragua	1	link	0
0	128	Níger	1	link	0
0	129	Nigeria	1	link	0
0	130	Noruega	1	link	0
0	131	Nueva Zelanda	1	link	0
0	132	Omán	1	link	0
0	133	Países Bajos	1	link	0
0	134	Pakistán	1	link	0
0	135	Palaos	1	link	0
0	136	Panamá	1	link	0
0	137	Papúa Nueva Guinea	1	link	0
0	138	Paraguay	1	link	0
0	139	Perú	1	link	0
0	140	Polonia	1	link	0
0	141	Portugal	1	link	0
0	142	Reino Unido	1	link	0
0	143	República Centroafricana	1	link	0
0	144	República Checa	1	link	0
0	145	República del Congo	1	link	0
0	146	República Dominicana	1	link	0
0	147	Ruanda	1	link	0
0	148	Rumania	1	link	0
0	149	Rusia	1	link	0
0	150	Samoa	1	link	0
0	151	San Cristóbal y Nieves	1	link	0
0	152	San Marino	1	link	0
0	153	San Vicente y las Granadinas	1	link	0
0	154	Santa Lucía	1	link	0
0	155	Santo Tomé y Príncipe	1	link	0
0	156	Senegal	1	link	0
0	157	Serbia	1	link	0
0	158	Seychelles	1	link	0
0	159	Sierra Leona	1	link	0
0	160	Singapur	1	link	0
0	161	Siria	1	link	0
0	162	Somalia	1	link	0
0	163	Sri Lanka	1	link	0
0	164	Sudáfrica	1	link	0
0	165	Sudán	1	link	0
0	166	Sudán del Sur	1	link	0
0	167	Suecia	1	link	0
0	168	Suiza	1	link	0
0	169	Surinam	1	link	0
0	170	Tailandia	1	link	0
0	171	Tanzania	1	link	0
0	172	Tayikistán	1	link	0
0	173	Timor Oriental	1	link	0
0	174	Togo	1	link	0
0	175	Tonga	1	link	0
0	176	Trinidad y Tobago	1	link	0
0	177	Túnez	1	link	0
0	178	Turkmenistán	1	link	0
0	179	Turquía	1	link	0
0	180	Tuvalu	1	link	0
0	181	Ucrania	1	link	0
0	182	Uganda	1	link	0
0	183	Uruguay	1	link	0
0	184	Uzbekistán	1	link	0
0	185	Vanuatu	1	link	0
0	186	Venezuela	1	link	0
0	187	Vietnam	1	link	0
0	188	Yemen	1	link	0
0	189	Yibuti	1	link	0
0	190	Zambia	1	link	0
0	191	Zimbabue	1	link	0
0	192	Alto Paraguay	2	link	0
0	193	Alto Paraná	2	link	0
0	194	Amambay	2	link	0
0	195	Boquerón	2	link	0
0	196	Caaguazú	2	link	0
0	197	Caazapá	2	link	0
0	198	Canindeyú	2	link	0
0	199	Central	2	link	0
0	200	Concepción	2	link	0
0	201	Cordillera	2	link	0
0	202	Guairá	2	link	0
0	203	Itapúa	2	link	0
0	204	Misiones	2	link	0
0	205	Ñeembucú	2	link	0
0	206	Paraguarí	2	link	0
0	207	Presidente Hayes	2	link	0
0	208	San Pedro	2	link	0
\.


--
-- Data for Name: _tabdelegados; Type: TABLE DATA; Schema: public; Owner: rebasedata
--

COPY public._tabdelegados ("idDelegado", "nomDelegado", "idDelegacion", "alumnoCEPB", "idCursoSeccion") FROM stdin;
\.


--
-- Data for Name: _tabmesa; Type: TABLE DATA; Schema: public; Owner: rebasedata
--

COPY public._tabmesa ("idSesion", "Presidente", "Moderador", "Secretario", "Evaluador", "Foro", "Año") FROM stdin;
\.


--
-- Data for Name: _tabobservaciones; Type: TABLE DATA; Schema: public; Owner: rebasedata
--

COPY public._tabobservaciones ("idSesion", "idObs", "descObs", "puntajeObs") FROM stdin;
\.


--
-- Data for Name: _tabpuntaje; Type: TABLE DATA; Schema: public; Owner: rebasedata
--

COPY public._tabpuntaje ("idSesion", "idPuntaje", "idDelegado", "idObs", "descObs", puntaje) FROM stdin;
\.


--
-- Data for Name: _tabsesion; Type: TABLE DATA; Schema: public; Owner: rebasedata
--

COPY public._tabsesion ("idSesion", "nomForo") FROM stdin;
\.


--
-- Data for Name: _tabtiempos; Type: TABLE DATA; Schema: public; Owner: rebasedata
--

COPY public._tabtiempos ("idSesion", leer, cuestionar, pensar, contestar) FROM stdin;
	60	30	30	60
\.


--
-- Data for Name: _tabtipodelegacion; Type: TABLE DATA; Schema: public; Owner: rebasedata
--

COPY public._tabtipodelegacion ("idTipoDelegacion", "nomTipoDelegacion") FROM stdin;
1	Pais
2	Departamento
\.


--
-- PostgreSQL database dump complete
--

