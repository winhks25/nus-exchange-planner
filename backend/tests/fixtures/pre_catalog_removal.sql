-- Generated from a disposable local database populated by the reviewed importer.
-- Includes one fixture-only duplicate mapping outside every degree membership.
--
-- PostgreSQL database dump
--

\restrict MOqgm9ZkoctfmYdWOrNk4BqhFjbCj4felQfEltmBRuG3bGnyVILzmMgmI73sn9p

-- Dumped from database version 15.15 (Homebrew)
-- Dumped by pg_dump version 15.15 (Homebrew)

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

--
-- Data for Name: catalog_import_batches; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.catalog_import_batches (id, source_checksum, repair_checksum, status, is_current, source_manifest, source_file_count, raw_row_count, accepted_row_count, repaired_row_count, quarantined_row_count, started_at, completed_at, note) OVERRIDING SYSTEM VALUE VALUES (1, 'b393cd0f6b34adb506a23ba810d65c083238339fab0b76a236167fdbef6901b9', '61268be6b39c1effc644d72c8cc4787287cdbcafc86d32fb3c48814d48064a3e', 'completed', true, '{"files": [{"kind": "manifest", "path": "backend/app/data_manifest.json", "sha256": "eafa0af73582f31afe4e30ef02f62284bd9bfce3425ddff679a7fef5d1d6400f", "byte_size": 224}, {"kind": "majors", "path": "data/majors/nus_soc_majors.json", "sha256": "f62a00b1f57bab9066e6629cbb20dabb0f43129d17c7bf456dc423933f04dfc4", "byte_size": 9798}, {"kind": "mapping", "path": "data/mapping/australia/west-au.json", "sha256": "987d1fe6343f72b41a51976f2767a0613b5028bb4371244863143ca8601aa95a", "byte_size": 10212}, {"kind": "mapping", "path": "data/mapping/canada/toronto.json", "sha256": "ad1baec1ee241b7b2ba253a65874615f66471abb384bf93a3fb66fc1430ddef9", "byte_size": 17338}, {"kind": "mapping", "path": "data/mapping/japan/kyoto.json", "sha256": "a42cb28be8372df929cd3c79b9860922ef15464758557689801ea004fdd48cd3", "byte_size": 2449}, {"kind": "mapping", "path": "data/mapping/korea/korea.json", "sha256": "96cdd005ff1d79923e7d3d19025bad6565f9a58dcf6dd6da16046e929b3a5946", "byte_size": 11348}, {"kind": "mapping", "path": "data/mapping/korea/yonsei.json", "sha256": "fd4b3635fa899f2e27c1a28592bf5c50f2908fe0992608d26d86a0c5ca269634", "byte_size": 7579}, {"kind": "repairs", "path": "data/repairs/catalog_repairs.json", "sha256": "61268be6b39c1effc644d72c8cc4787287cdbcafc86d32fb3c48814d48064a3e", "byte_size": 20732}], "prepared_on": "2026-10-22", "repair_file": "data/repairs/catalog_repairs.json", "academic_year": "AY2026/27", "repair_checksum_sha256": "61268be6b39c1effc644d72c8cc4787287cdbcafc86d32fb3c48814d48064a3e", "source_checksum_sha256": "b393cd0f6b34adb506a23ba810d65c083238339fab0b76a236167fdbef6901b9"}', 8, 155, 147, 5, 3, '2026-10-23 23:01:40.872227+08', '2026-10-23 23:01:40.872227+08', 'Initial publication completed from the reviewed import plan.');


--
-- Data for Name: catalog_source_snapshots; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.catalog_source_snapshots (id, batch_id, file_path, source_kind, raw_text, parsed_json, sha256, byte_size, archived_at) OVERRIDING SYSTEM VALUE VALUES (1, 1, 'backend/app/data_manifest.json', 'manifest', '{
  "files": [
    "majors/nus_soc_majors.json",
    "mapping/australia/west-au.json",
    "mapping/canada/toronto.json",
    "mapping/japan/kyoto.json",
    "mapping/korea/korea.json",
    "mapping/korea/yonsei.json"
  ]
}
', '{"files": ["majors/nus_soc_majors.json", "mapping/australia/west-au.json", "mapping/canada/toronto.json", "mapping/japan/kyoto.json", "mapping/korea/korea.json", "mapping/korea/yonsei.json"]}', 'eafa0af73582f31afe4e30ef02f62284bd9bfce3425ddff679a7fef5d1d6400f', 224, '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_snapshots (id, batch_id, file_path, source_kind, raw_text, parsed_json, sha256, byte_size, archived_at) OVERRIDING SYSTEM VALUE VALUES (2, 1, 'data/majors/nus_soc_majors.json', 'majors', '{
  "institution": "National University of Singapore",
  "school": "School of Computing",
  "academic_year": "AY2026/27 website snapshot",
  "source_index": "https://www.comp.nus.edu.sg/programmes/",
  "notes": [
    "Includes six standalone SoC computing majors with curriculum pages: Artificial Intelligence, Business Analytics, Business Artificial Intelligence Systems, Computer Science, Information Systems, and Information Security. Computer Engineering is a joint programme with CDE; Geospatial Intelligence is offered by CHS.",
    "The pages contain cohort-specific/advisory material; check the linked official curriculum before planning enrolment. Common Curriculum and unrestricted electives are summarized separately from major programme requirements.",
    "Modules listed under elective lists are the complete prescribed lists shown on the source pages; selection and unit/level constraints apply. Titles follow the NUS pages where available."
  ],
  "majors": [
    {
      "name": "Artificial Intelligence",
      "degree": "Bachelor of Computing (Artificial Intelligence)",
      "code": "BComp(AI)",
      "curriculum_url": "https://www.comp.nus.edu.sg/programmes/ug/ai/curr/",
      "degree_units": 160,
      "common_curriculum_units": 40,
      "unrestricted_elective_units": 40,
      "programme_requirements_units": 80,
      "required": {
        "computing_foundations": ["CS2030S", "CS2040S", "CS2101", "CS2103T", "CS3230"],
        "ai_foundations": ["CS2109S", "CS3263", "CS3264", "CS3268"],
        "perception_choose_one": ["CS4243", "CS4248"],
        "mathematics_foundations": ["CS1231S", "CS2251", "MA1521", "MA1522", "ST2334"]
      },
      "electives": {
        "ai_technical_electives_choose_min_12_units": ["CS4220", "CS4225", "CS4240", "CS4244", "CS4246", "CS4261", "CS4262", "CS4347", "CS4277", "CS4278"],
        "breadth_depth": "20 units total; at least 12 units at level 4000 or above; industrial experience 6–12 units (eligible students may replace with CP4101 dissertation); other constraints apply."
      },
      "source_detail": "CS2101/CS2103T are a twinned pair."
    },
    {
      "name": "Business Analytics",
      "degree": "Bachelor of Science (Business Analytics)",
      "code": "BSc(BA)",
      "curriculum_url": "https://www.comp.nus.edu.sg/programmes/ug/ba/curr/",
      "degree_units": 160,
      "common_curriculum_units": 40,
      "unrestricted_elective_units": 40,
      "programme_requirements_units": 80,
      "required": {
        "core": ["MA1521", "MA1522", "BT2101", "BT2102", "CS2030", "CS2040", "IS2101", "ST2334", "BT3103", "IS3103", "BT4103", "BT4101 or Industrial Experience Requirement"]
      },
      "electives": {
        "programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded": {
          "business_applications": ["IE3120", "IS3150", "IS3240", "BT4013", "BT4016", "BT4211", "BT4212", "DBA4811", "IS4241", "IS4242", "IS4250", "IS4262"],
          "methodological_analytics": ["BT3017", "BT3102", "BT3104", "CP3100", "CS3243", "CS3244", "CS4248", "BT4012", "BT4015", "BT4221", "BT4222", "BT4240", "BT4241", "IS4241", "ST4245"],
          "digital_and_it": ["IS3107", "IS3221", "BT4014", "BT4301", "IS4226", "IS4228", "IS4234", "IS4246", "IS4302", "IS4303"]
        },
        "specialisations": {
          "Financial Analytics": ["BT3102", "BT4012", "BT4013", "BT4016", "BT4221", "IS4226", "IS4228", "IS4234", "IS4302", "IS4303"],
          "Machine Learning-based Analytics": ["BT3017", "BT4012", "BT4014", "BT4221", "BT4222", "BT4240", "BT4241", "BT4301", "CS3243", "CS4248", "IS4246"],
          "Marketing Analytics": ["BT3017", "BT4014", "BT4015", "BT4211", "BT4212", "BT4222", "IS3150", "IS4241", "IS4262"]
        }
      },
      "source_detail": "Specialisations are optional; five programme electives remain required."
    },
    {
      "name": "Business Artificial Intelligence Systems",
      "degree": "Bachelor of Computing (Business Artificial Intelligence Systems)",
      "code": "BComp(BAIS)",
      "curriculum_url": "https://www.comp.nus.edu.sg/programmes/ug/bais/curr/",
      "degree_units": 160,
      "common_curriculum_units": 40,
      "unrestricted_elective_units": 40,
      "programme_requirements_units": 80,
      "required": {
        "core": ["BT2102", "CS2030", "CS2040", "IS2101", "IS2108", "IS2109", "IS3103", "Industry Experience Requirement or CP4101", "IS4108", "MA1521", "MA1522", "ST2334"]
      },
      "electives": {
        "programme_electives_choose_5_20_units_at_least_3_level_4000": ["IS3150", "IS3240", "IS4262", "IS4226", "IS4228", "IS4302", "IS4303", "CS2105", "IS2102", "IS3108", "IS3221", "IS4100", "IS4234", "IS4236", "IS4243", "IS4248", "IS4250", "IS4301", "BT3017", "BT4014", "BT4221", "BT4301", "IS3107", "IS3109", "IS4151", "IS4246", "IS4400", "IS4401", "IS4402", "IS4403", "CP3100", "IS3251", "IS4152", "IS4241", "IS4261", "CS2107", "IFS4101", "IS4231", "IS4233", "IS4238"],
        "specialisations": {
          "AI Governance and Management": "See official curriculum page for prescribed course list.",
          "Digital Product and Platform Management": "See official curriculum page for prescribed course list.",
          "Financial Technology": "See official curriculum page for prescribed course list."
        }
      },
      "source_detail": "NUS describes this as formerly the Bachelor of Computing in Information Systems; it is listed as its own current programme. The elective page groups options under specialisation headings."
    },
    {
      "name": "Computer Science",
      "degree": "Bachelor of Computing (Computer Science)",
      "code": "BComp(CS)",
      "curriculum_url": "https://www.comp.nus.edu.sg/programmes/ug/cs/curr/",
      "degree_units": 160,
      "common_curriculum_units": 40,
      "unrestricted_elective_units": 40,
      "programme_requirements_units": 80,
      "required": {
        "computer_science_foundation": ["CS1231S", "CS2030S", "CS2040S", "CS2100", "CS2101", "CS2103T", "CS2106", "CS2109S", "CS3230"],
        "mathematics_and_sciences": ["MA1521", "MA1522", "ST2334"]
      },
      "electives": {
        "breadth_depth": "32 units of computing courses; satisfy one Focus Area through 3 Area Primary courses (at least one level 4000+), at least 12 units level 4000+, and 6–12 units Industry Experience (eligible students may replace with CP4101 dissertation). CS/IFS/CP coding constraints apply.",
        "focus_areas": ["Algorithms & Theory", "Artificial Intelligence", "Computer Graphics and Games", "Computer Security", "Database Systems", "Multimedia Information Retrieval", "Networking and Distributed Systems", "Parallel Computing", "Programming Languages", "Software Engineering"],
        "all_electives": "The complete course-by-course Area Primaries/elective catalog is linked from the curriculum page (Focus Areas details); use that live catalog because offerings change."
      },
      "source_detail": "CS2101 and CS2103T must be taken in the same semester."
    },
    {
      "name": "Information Systems",
      "degree": "Bachelor of Computing (Information Systems)",
      "code": "BComp(IS)",
      "curriculum_url": "https://www.comp.nus.edu.sg/programmes/ug/is/curr/",
      "degree_units": 160,
      "common_curriculum_units": 40,
      "unrestricted_elective_units": 40,
      "programme_requirements_units": 80,
      "required": {
        "core": ["BT2102 or CS2102", "CS2030", "CS2040", "IS2101", "IS2102", "IS2103", "IS3103", "IS3106", "CP4101 or Industrial Experience Requirement", "IS4103", "MA1521", "ST2334"]
      },
      "electives": {
        "programme_electives_choose_5_20_units_at_least_3_level_4000": ["IS3150", "IS3240", "IS4151", "IS4262", "IS4226", "IS4228", "IS4302", "IS4303", "CS2105", "BT3017", "CS3240", "CS3243", "IS3107", "IS3221", "BT4014", "IS4100", "IS4234", "IS4236", "IS4243", "IS4246", "IS4248", "IS4250", "IS4301", "IS3251", "IS4152", "IS4241", "IS4242", "IS4261", "CS2107", "IFS4101", "IS4231", "IS4233", "IS4238"],
        "specialisations": {
          "Digital Product and Platform Management": "Optional; consult official specialisation list.",
          "Financial Technology": "Optional; consult official specialisation list.",
          "Intelligent Systems Solutioning": "Optional; consult official specialisation list."
        }
      },
      "source_detail": "IS and BAIS have distinct published programme pages; confirm applicable cohort because BAIS is described as the successor/renamed programme."
    },
    {
      "name": "Information Security",
      "degree": "Bachelor of Computing (Information Security)",
      "code": "BComp(InfoSec)",
      "curriculum_url": "https://www.comp.nus.edu.sg/programmes/ug/isc/curr/",
      "degree_units": 160,
      "common_curriculum_units": 40,
      "unrestricted_elective_units": 36,
      "programme_requirements_units": 84,
      "required": {
        "computing_foundation": ["CS1231S", "CS2030", "CS2040C", "CS2100", "CS2101", "CS2103T", "CS2105", "CS2106"],
        "information_security": ["CS2107", "CS3235", "IFS4205 or (CS4238 and IFS4103)", "IS4231"],
        "mathematics": ["MA1521", "MA1522", "ST2334"],
        "computing_requirement": "12 units CS/IS/CP-coded; CS- and IS-coded courses must be level 3000+; at least 6 units must be industrial experience."
      },
      "electives": {
        "information_security_electives_choose_8_units": ["CS4230", "CS4236 or MA4261", "CS4238", "CS4239", "CS4257", "CS4276", "CS5231", "CS5321", "CS5322", "CS5331", "CS5332", "IFS4101", "IFS4102", "IFS4103", "IS4204", "IS4233", "IS4234", "IS4238", "IS4302", "other level-4000+ courses approved by SoC UG Office"],
        "industry_experience": ["CP3880", "IS4010", "TR3202", "CP3200", "CP3202", "CP3107", "CP3110"]
      }
    }
  ]
}
', '{"notes": ["Includes six standalone SoC computing majors with curriculum pages: Artificial Intelligence, Business Analytics, Business Artificial Intelligence Systems, Computer Science, Information Systems, and Information Security. Computer Engineering is a joint programme with CDE; Geospatial Intelligence is offered by CHS.", "The pages contain cohort-specific/advisory material; check the linked official curriculum before planning enrolment. Common Curriculum and unrestricted electives are summarized separately from major programme requirements.", "Modules listed under elective lists are the complete prescribed lists shown on the source pages; selection and unit/level constraints apply. Titles follow the NUS pages where available."], "majors": [{"code": "BComp(AI)", "name": "Artificial Intelligence", "degree": "Bachelor of Computing (Artificial Intelligence)", "required": {"ai_foundations": ["CS2109S", "CS3263", "CS3264", "CS3268"], "computing_foundations": ["CS2030S", "CS2040S", "CS2101", "CS2103T", "CS3230"], "perception_choose_one": ["CS4243", "CS4248"], "mathematics_foundations": ["CS1231S", "CS2251", "MA1521", "MA1522", "ST2334"]}, "electives": {"breadth_depth": "20 units total; at least 12 units at level 4000 or above; industrial experience 6–12 units (eligible students may replace with CP4101 dissertation); other constraints apply.", "ai_technical_electives_choose_min_12_units": ["CS4220", "CS4225", "CS4240", "CS4244", "CS4246", "CS4261", "CS4262", "CS4347", "CS4277", "CS4278"]}, "degree_units": 160, "source_detail": "CS2101/CS2103T are a twinned pair.", "curriculum_url": "https://www.comp.nus.edu.sg/programmes/ug/ai/curr/", "common_curriculum_units": 40, "unrestricted_elective_units": 40, "programme_requirements_units": 80}, {"code": "BSc(BA)", "name": "Business Analytics", "degree": "Bachelor of Science (Business Analytics)", "required": {"core": ["MA1521", "MA1522", "BT2101", "BT2102", "CS2030", "CS2040", "IS2101", "ST2334", "BT3103", "IS3103", "BT4103", "BT4101 or Industrial Experience Requirement"]}, "electives": {"specialisations": {"Financial Analytics": ["BT3102", "BT4012", "BT4013", "BT4016", "BT4221", "IS4226", "IS4228", "IS4234", "IS4302", "IS4303"], "Marketing Analytics": ["BT3017", "BT4014", "BT4015", "BT4211", "BT4212", "BT4222", "IS3150", "IS4241", "IS4262"], "Machine Learning-based Analytics": ["BT3017", "BT4012", "BT4014", "BT4221", "BT4222", "BT4240", "BT4241", "BT4301", "CS3243", "CS4248", "IS4246"]}, "programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded": {"digital_and_it": ["IS3107", "IS3221", "BT4014", "BT4301", "IS4226", "IS4228", "IS4234", "IS4246", "IS4302", "IS4303"], "business_applications": ["IE3120", "IS3150", "IS3240", "BT4013", "BT4016", "BT4211", "BT4212", "DBA4811", "IS4241", "IS4242", "IS4250", "IS4262"], "methodological_analytics": ["BT3017", "BT3102", "BT3104", "CP3100", "CS3243", "CS3244", "CS4248", "BT4012", "BT4015", "BT4221", "BT4222", "BT4240", "BT4241", "IS4241", "ST4245"]}}, "degree_units": 160, "source_detail": "Specialisations are optional; five programme electives remain required.", "curriculum_url": "https://www.comp.nus.edu.sg/programmes/ug/ba/curr/", "common_curriculum_units": 40, "unrestricted_elective_units": 40, "programme_requirements_units": 80}, {"code": "BComp(BAIS)", "name": "Business Artificial Intelligence Systems", "degree": "Bachelor of Computing (Business Artificial Intelligence Systems)", "required": {"core": ["BT2102", "CS2030", "CS2040", "IS2101", "IS2108", "IS2109", "IS3103", "Industry Experience Requirement or CP4101", "IS4108", "MA1521", "MA1522", "ST2334"]}, "electives": {"specialisations": {"Financial Technology": "See official curriculum page for prescribed course list.", "AI Governance and Management": "See official curriculum page for prescribed course list.", "Digital Product and Platform Management": "See official curriculum page for prescribed course list."}, "programme_electives_choose_5_20_units_at_least_3_level_4000": ["IS3150", "IS3240", "IS4262", "IS4226", "IS4228", "IS4302", "IS4303", "CS2105", "IS2102", "IS3108", "IS3221", "IS4100", "IS4234", "IS4236", "IS4243", "IS4248", "IS4250", "IS4301", "BT3017", "BT4014", "BT4221", "BT4301", "IS3107", "IS3109", "IS4151", "IS4246", "IS4400", "IS4401", "IS4402", "IS4403", "CP3100", "IS3251", "IS4152", "IS4241", "IS4261", "CS2107", "IFS4101", "IS4231", "IS4233", "IS4238"]}, "degree_units": 160, "source_detail": "NUS describes this as formerly the Bachelor of Computing in Information Systems; it is listed as its own current programme. The elective page groups options under specialisation headings.", "curriculum_url": "https://www.comp.nus.edu.sg/programmes/ug/bais/curr/", "common_curriculum_units": 40, "unrestricted_elective_units": 40, "programme_requirements_units": 80}, {"code": "BComp(CS)", "name": "Computer Science", "degree": "Bachelor of Computing (Computer Science)", "required": {"mathematics_and_sciences": ["MA1521", "MA1522", "ST2334"], "computer_science_foundation": ["CS1231S", "CS2030S", "CS2040S", "CS2100", "CS2101", "CS2103T", "CS2106", "CS2109S", "CS3230"]}, "electives": {"focus_areas": ["Algorithms & Theory", "Artificial Intelligence", "Computer Graphics and Games", "Computer Security", "Database Systems", "Multimedia Information Retrieval", "Networking and Distributed Systems", "Parallel Computing", "Programming Languages", "Software Engineering"], "all_electives": "The complete course-by-course Area Primaries/elective catalog is linked from the curriculum page (Focus Areas details); use that live catalog because offerings change.", "breadth_depth": "32 units of computing courses; satisfy one Focus Area through 3 Area Primary courses (at least one level 4000+), at least 12 units level 4000+, and 6–12 units Industry Experience (eligible students may replace with CP4101 dissertation). CS/IFS/CP coding constraints apply."}, "degree_units": 160, "source_detail": "CS2101 and CS2103T must be taken in the same semester.", "curriculum_url": "https://www.comp.nus.edu.sg/programmes/ug/cs/curr/", "common_curriculum_units": 40, "unrestricted_elective_units": 40, "programme_requirements_units": 80}, {"code": "BComp(IS)", "name": "Information Systems", "degree": "Bachelor of Computing (Information Systems)", "required": {"core": ["BT2102 or CS2102", "CS2030", "CS2040", "IS2101", "IS2102", "IS2103", "IS3103", "IS3106", "CP4101 or Industrial Experience Requirement", "IS4103", "MA1521", "ST2334"]}, "electives": {"specialisations": {"Financial Technology": "Optional; consult official specialisation list.", "Intelligent Systems Solutioning": "Optional; consult official specialisation list.", "Digital Product and Platform Management": "Optional; consult official specialisation list."}, "programme_electives_choose_5_20_units_at_least_3_level_4000": ["IS3150", "IS3240", "IS4151", "IS4262", "IS4226", "IS4228", "IS4302", "IS4303", "CS2105", "BT3017", "CS3240", "CS3243", "IS3107", "IS3221", "BT4014", "IS4100", "IS4234", "IS4236", "IS4243", "IS4246", "IS4248", "IS4250", "IS4301", "IS3251", "IS4152", "IS4241", "IS4242", "IS4261", "CS2107", "IFS4101", "IS4231", "IS4233", "IS4238"]}, "degree_units": 160, "source_detail": "IS and BAIS have distinct published programme pages; confirm applicable cohort because BAIS is described as the successor/renamed programme.", "curriculum_url": "https://www.comp.nus.edu.sg/programmes/ug/is/curr/", "common_curriculum_units": 40, "unrestricted_elective_units": 40, "programme_requirements_units": 80}, {"code": "BComp(InfoSec)", "name": "Information Security", "degree": "Bachelor of Computing (Information Security)", "required": {"mathematics": ["MA1521", "MA1522", "ST2334"], "computing_foundation": ["CS1231S", "CS2030", "CS2040C", "CS2100", "CS2101", "CS2103T", "CS2105", "CS2106"], "information_security": ["CS2107", "CS3235", "IFS4205 or (CS4238 and IFS4103)", "IS4231"], "computing_requirement": "12 units CS/IS/CP-coded; CS- and IS-coded courses must be level 3000+; at least 6 units must be industrial experience."}, "electives": {"industry_experience": ["CP3880", "IS4010", "TR3202", "CP3200", "CP3202", "CP3107", "CP3110"], "information_security_electives_choose_8_units": ["CS4230", "CS4236 or MA4261", "CS4238", "CS4239", "CS4257", "CS4276", "CS5231", "CS5321", "CS5322", "CS5331", "CS5332", "IFS4101", "IFS4102", "IFS4103", "IS4204", "IS4233", "IS4234", "IS4238", "IS4302", "other level-4000+ courses approved by SoC UG Office"]}, "degree_units": 160, "curriculum_url": "https://www.comp.nus.edu.sg/programmes/ug/isc/curr/", "common_curriculum_units": 40, "unrestricted_elective_units": 36, "programme_requirements_units": 84}], "school": "School of Computing", "institution": "National University of Singapore", "source_index": "https://www.comp.nus.edu.sg/programmes/", "academic_year": "AY2026/27 website snapshot"}', 'f62a00b1f57bab9066e6629cbb20dabb0f43129d17c7bf456dc423933f04dfc4', 9798, '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_snapshots (id, batch_id, file_path, source_kind, raw_text, parsed_json, sha256, byte_size, archived_at) OVERRIDING SYSTEM VALUE VALUES (3, 1, 'data/mapping/australia/west-au.json', 'mapping', '{
  "partner_university": {
    "name": "University of Western Australia",
    "edurec_id": "E0000000618"
  },
  "source": {
    "file": "west-au.pdf",
    "system": "NUS EduRec Course Mappings Search",
    "retrieved_at": "2026-10-14"
  },
  "mapping_count": 32,
  "mappings": [
    {
      "partner_course": {
        "code": "BUSN5001",
        "title": "Blockchain and Distributed Ledger Technologies in Business",
        "units": 6.0
      },
      "nus_course": {
        "code": "IS4302",
        "title": "Blockchain and Distributed"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CITS1402",
        "title": "Relational Database Management Systems",
        "units": 6.0
      },
      "nus_course": {
        "code": "CS2102",
        "title": "Database Systems"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CITS2200",
        "title": "Data Structures and Algorithms",
        "units": 6.0
      },
      "nus_course": {
        "code": "CS2040",
        "title": "Data Structures and Algor"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CITS3001",
        "title": "Algorithms, Agents and Artificial Intelligence",
        "units": 6.0
      },
      "nus_course": {
        "code": "BT4014",
        "title": "Analytics Driven Design of"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CITS3001",
        "title": "Algorithms, Agents and Artificial Intelligence",
        "units": 6.0
      },
      "nus_course": {
        "code": "CS3243",
        "title": "Introduction to Artificial In"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CITS3002",
        "title": "Computer Networks",
        "units": 6.0
      },
      "nus_course": {
        "code": "CS2105",
        "title": "Introduction to Computer"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CITS3004",
        "title": "Cybersecurity",
        "units": 6.0
      },
      "nus_course": {
        "code": "CS3235",
        "title": "Computer Security"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CITS3006",
        "title": "Penetration Testing",
        "units": 6.0
      },
      "nus_course": {
        "code": "IFS4103",
        "title": "Penetration Testing Practic"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CITS3007",
        "title": "Secure Coding",
        "units": 6.0
      },
      "nus_course": {
        "code": "CS4239",
        "title": "Software Security"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CITS3301",
        "title": "Software Requirements and Design",
        "units": 6.0
      },
      "nus_course": {
        "code": "CS3213",
        "title": "Software Requirements Sp"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CITS4009",
        "title": "Computational Data Analysis",
        "units": 6.0
      },
      "nus_course": {
        "code": "BT4014",
        "title": "Analytics Driven Design of"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CITS4404",
        "title": "Artificial Intelligence and Adaptive Systems",
        "units": 6.0
      },
      "nus_course": {
        "code": "BT4014",
        "title": "Analytics Driven Design of"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CITS4404",
        "title": "Artificial Intelligence and Adaptive Systems",
        "units": 6.0
      },
      "nus_course": {
        "code": "CS3243",
        "title": "Introduction to Artificial In"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CITS4404",
        "title": "Artificial Intelligence and Adaptive Systems",
        "units": 6.0
      },
      "nus_course": {
        "code": "IS4242",
        "title": "Intelligent Systems and Te"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CITS4419",
        "title": "Mobile and Wireless Computing",
        "units": 6.0
      },
      "nus_course": {
        "code": "CS4222",
        "title": "Wireless Networking"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CITS5503",
        "title": "Cloud Computing",
        "units": 6.0
      },
      "nus_course": {
        "code": "CS5224",
        "title": "Cloud Computing"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CITS5506",
        "title": "The Internet of Things",
        "units": 6.0
      },
      "nus_course": {
        "code": "CS3237",
        "title": "Introduction to Internet of"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CITS5507",
        "title": "High Performance Computing",
        "units": 6.0
      },
      "nus_course": {
        "code": "CS3210",
        "title": "Parallel Computing"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CTIS2005",
        "title": "Object Oriented Programming",
        "units": 6.0
      },
      "nus_course": {
        "code": "CS2030",
        "title": "Programming Methodology"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "ENVT4411",
        "title": "Geographic Information Systems Applications",
        "units": 6.0
      },
      "nus_course": {
        "code": "BT4015",
        "title": "Geospatial Analytics"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "ENVT5566",
        "title": "Advanced Spatial and Environmental Modelling",
        "units": 6.0
      },
      "nus_course": {
        "code": "BT4015",
        "title": "Geospatial Analytics"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "FINA4491",
        "title": "Capital Markets Research",
        "units": 6.0
      },
      "nus_course": {
        "code": "BT4013",
        "title": "Analytics for Capital Marke"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "GEOG2201",
        "title": "Geographic Information Systems",
        "units": 6.0
      },
      "nus_course": {
        "code": "BT4015",
        "title": "Geospatial Analytics"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "GEOG3300",
        "title": "Advanced Spatial Analysis",
        "units": 6.0
      },
      "nus_course": {
        "code": "BT4015",
        "title": "Geospatial Analytics"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "MATH3002",
        "title": "Network Science",
        "units": 6.0
      },
      "nus_course": {
        "code": "IS4241",
        "title": "Social Media Network Ana"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "MKTG2305",
        "title": "Marketing Research",
        "units": 6.0
      },
      "nus_course": {
        "code": "BT4211",
        "title": "Data-Driven Marketing"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "MKTG3307",
        "title": "Digital Marketing",
        "units": 6.0
      },
      "nus_course": {
        "code": "BT4211",
        "title": "Data-Driven Marketing"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "MKTG3308",
        "title": "Marketing Analytics",
        "units": 6.0
      },
      "nus_course": {
        "code": "BT4211",
        "title": "Data-Driven Marketing"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "MKTG5504",
        "title": "Big Data in Marketing",
        "units": 6.0
      },
      "nus_course": {
        "code": "BT4211",
        "title": "Data-Driven Marketing"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "STAT3063",
        "title": "Spatial Statistics and Modeling",
        "units": 6.0
      },
      "nus_course": {
        "code": "BT4015",
        "title": "Geospatial Analytics"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "STAT3406",
        "title": "Applied Statistics and Data Visualisation",
        "units": 6.0
      },
      "nus_course": {
        "code": "BT4240",
        "title": "Machine Learning for Pred"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "STAT4064",
        "title": "Applied Predictive Modeling",
        "units": 6.0
      },
      "nus_course": {
        "code": "BT4240",
        "title": "Machine Learning for Pred"
      },
      "faculty": "School of Computing",
      "source_page": 1
    }
  ]
}
', '{"source": {"file": "west-au.pdf", "system": "NUS EduRec Course Mappings Search", "retrieved_at": "2026-10-14"}, "mappings": [{"faculty": "School of Computing", "nus_course": {"code": "IS4302", "title": "Blockchain and Distributed"}, "source_page": 1, "partner_course": {"code": "BUSN5001", "title": "Blockchain and Distributed Ledger Technologies in Business", "units": 6.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS2102", "title": "Database Systems"}, "source_page": 1, "partner_course": {"code": "CITS1402", "title": "Relational Database Management Systems", "units": 6.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS2040", "title": "Data Structures and Algor"}, "source_page": 1, "partner_course": {"code": "CITS2200", "title": "Data Structures and Algorithms", "units": 6.0}}, {"faculty": "School of Computing", "nus_course": {"code": "BT4014", "title": "Analytics Driven Design of"}, "source_page": 1, "partner_course": {"code": "CITS3001", "title": "Algorithms, Agents and Artificial Intelligence", "units": 6.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3243", "title": "Introduction to Artificial In"}, "source_page": 1, "partner_course": {"code": "CITS3001", "title": "Algorithms, Agents and Artificial Intelligence", "units": 6.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS2105", "title": "Introduction to Computer"}, "source_page": 1, "partner_course": {"code": "CITS3002", "title": "Computer Networks", "units": 6.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3235", "title": "Computer Security"}, "source_page": 1, "partner_course": {"code": "CITS3004", "title": "Cybersecurity", "units": 6.0}}, {"faculty": "School of Computing", "nus_course": {"code": "IFS4103", "title": "Penetration Testing Practic"}, "source_page": 1, "partner_course": {"code": "CITS3006", "title": "Penetration Testing", "units": 6.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS4239", "title": "Software Security"}, "source_page": 1, "partner_course": {"code": "CITS3007", "title": "Secure Coding", "units": 6.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3213", "title": "Software Requirements Sp"}, "source_page": 1, "partner_course": {"code": "CITS3301", "title": "Software Requirements and Design", "units": 6.0}}, {"faculty": "School of Computing", "nus_course": {"code": "BT4014", "title": "Analytics Driven Design of"}, "source_page": 1, "partner_course": {"code": "CITS4009", "title": "Computational Data Analysis", "units": 6.0}}, {"faculty": "School of Computing", "nus_course": {"code": "BT4014", "title": "Analytics Driven Design of"}, "source_page": 1, "partner_course": {"code": "CITS4404", "title": "Artificial Intelligence and Adaptive Systems", "units": 6.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3243", "title": "Introduction to Artificial In"}, "source_page": 1, "partner_course": {"code": "CITS4404", "title": "Artificial Intelligence and Adaptive Systems", "units": 6.0}}, {"faculty": "School of Computing", "nus_course": {"code": "IS4242", "title": "Intelligent Systems and Te"}, "source_page": 1, "partner_course": {"code": "CITS4404", "title": "Artificial Intelligence and Adaptive Systems", "units": 6.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS4222", "title": "Wireless Networking"}, "source_page": 1, "partner_course": {"code": "CITS4419", "title": "Mobile and Wireless Computing", "units": 6.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS5224", "title": "Cloud Computing"}, "source_page": 1, "partner_course": {"code": "CITS5503", "title": "Cloud Computing", "units": 6.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3237", "title": "Introduction to Internet of"}, "source_page": 1, "partner_course": {"code": "CITS5506", "title": "The Internet of Things", "units": 6.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3210", "title": "Parallel Computing"}, "source_page": 1, "partner_course": {"code": "CITS5507", "title": "High Performance Computing", "units": 6.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS2030", "title": "Programming Methodology"}, "source_page": 1, "partner_course": {"code": "CTIS2005", "title": "Object Oriented Programming", "units": 6.0}}, {"faculty": "School of Computing", "nus_course": {"code": "BT4015", "title": "Geospatial Analytics"}, "source_page": 1, "partner_course": {"code": "ENVT4411", "title": "Geographic Information Systems Applications", "units": 6.0}}, {"faculty": "School of Computing", "nus_course": {"code": "BT4015", "title": "Geospatial Analytics"}, "source_page": 1, "partner_course": {"code": "ENVT5566", "title": "Advanced Spatial and Environmental Modelling", "units": 6.0}}, {"faculty": "School of Computing", "nus_course": {"code": "BT4013", "title": "Analytics for Capital Marke"}, "source_page": 1, "partner_course": {"code": "FINA4491", "title": "Capital Markets Research", "units": 6.0}}, {"faculty": "School of Computing", "nus_course": {"code": "BT4015", "title": "Geospatial Analytics"}, "source_page": 1, "partner_course": {"code": "GEOG2201", "title": "Geographic Information Systems", "units": 6.0}}, {"faculty": "School of Computing", "nus_course": {"code": "BT4015", "title": "Geospatial Analytics"}, "source_page": 1, "partner_course": {"code": "GEOG3300", "title": "Advanced Spatial Analysis", "units": 6.0}}, {"faculty": "School of Computing", "nus_course": {"code": "IS4241", "title": "Social Media Network Ana"}, "source_page": 1, "partner_course": {"code": "MATH3002", "title": "Network Science", "units": 6.0}}, {"faculty": "School of Computing", "nus_course": {"code": "BT4211", "title": "Data-Driven Marketing"}, "source_page": 1, "partner_course": {"code": "MKTG2305", "title": "Marketing Research", "units": 6.0}}, {"faculty": "School of Computing", "nus_course": {"code": "BT4211", "title": "Data-Driven Marketing"}, "source_page": 1, "partner_course": {"code": "MKTG3307", "title": "Digital Marketing", "units": 6.0}}, {"faculty": "School of Computing", "nus_course": {"code": "BT4211", "title": "Data-Driven Marketing"}, "source_page": 1, "partner_course": {"code": "MKTG3308", "title": "Marketing Analytics", "units": 6.0}}, {"faculty": "School of Computing", "nus_course": {"code": "BT4211", "title": "Data-Driven Marketing"}, "source_page": 1, "partner_course": {"code": "MKTG5504", "title": "Big Data in Marketing", "units": 6.0}}, {"faculty": "School of Computing", "nus_course": {"code": "BT4015", "title": "Geospatial Analytics"}, "source_page": 1, "partner_course": {"code": "STAT3063", "title": "Spatial Statistics and Modeling", "units": 6.0}}, {"faculty": "School of Computing", "nus_course": {"code": "BT4240", "title": "Machine Learning for Pred"}, "source_page": 1, "partner_course": {"code": "STAT3406", "title": "Applied Statistics and Data Visualisation", "units": 6.0}}, {"faculty": "School of Computing", "nus_course": {"code": "BT4240", "title": "Machine Learning for Pred"}, "source_page": 1, "partner_course": {"code": "STAT4064", "title": "Applied Predictive Modeling", "units": 6.0}}], "mapping_count": 32, "partner_university": {"name": "University of Western Australia", "edurec_id": "E0000000618"}}', '987d1fe6343f72b41a51976f2767a0613b5028bb4371244863143ca8601aa95a', 10212, '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_snapshots (id, batch_id, file_path, source_kind, raw_text, parsed_json, sha256, byte_size, archived_at) OVERRIDING SYSTEM VALUE VALUES (4, 1, 'data/mapping/canada/toronto.json', 'mapping', '{
  "partner_university": {
    "name": "University of Toronto",
    "edurec_id": "E0000000684"
  },
  "source": {
    "file": "toronto.pdf",
    "system": "NUS EduRec Course Mappings Search",
    "retrieved_at": "2026-10-14"
  },
  "mapping_count": 55,
  "mappings": [
    {
      "partner_course": {
        "code": "ECE344H1",
        "title": "Operating Systems",
        "units": 0.5
      },
      "nus_course": {
        "code": "CS2106",
        "title": "Introduction to Operating"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC444H1",
        "title": "Software Engineering",
        "units": 0.5
      },
      "nus_course": {
        "code": "CS2103",
        "title": "Software Engineering"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC326H1",
        "title": "Programming Languages",
        "units": 0.5
      },
      "nus_course": {
        "code": "CS2104",
        "title": "Programming Language C"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC404H1",
        "title": "Introduction to Video Game Design",
        "units": 0.5
      },
      "nus_course": {
        "code": "CS3247",
        "title": "Game Development"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "ROB313H1",
        "title": "Introduction to Learning from Data",
        "units": 0.5
      },
      "nus_course": {
        "code": "CS3244",
        "title": "Machine Learning"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC428H1-S",
        "title": "Human-Computer Interaction",
        "units": 0.5
      },
      "nus_course": {
        "code": "CS4249",
        "title": "Quantitative Methods of H"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC420H1",
        "title": "Introduction to Image Understanding",
        "units": 0.5
      },
      "nus_course": {
        "code": "CS4243",
        "title": "Computer Vision and Patte"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC413H1",
        "title": "\" Neural Networks and Deep Learning\"",
        "units": 0.5
      },
      "nus_course": {
        "code": "CS5242",
        "title": "Neural Networks and Deep"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC309H1",
        "title": "Programming on the Web",
        "units": 0.5
      },
      "nus_course": {
        "code": "BT3103",
        "title": "Application Systems Deve"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC412",
        "title": "Probabilistic Learning and Reasoning",
        "units": 0.5
      },
      "nus_course": {
        "code": "BT3102",
        "title": "Computational Methods fo"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC443H1",
        "title": "Database System Technology",
        "units": 0.5
      },
      "nus_course": {
        "code": "IS3107",
        "title": "Data Engineering"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC311H1",
        "title": "Introduction to Machine Learning",
        "units": 0.5
      },
      "nus_course": {
        "code": "CS3264",
        "title": "Foundations of Machine Le"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC401H1",
        "title": "Natural Language Computing",
        "units": 0.5
      },
      "nus_course": {
        "code": "CS4248",
        "title": "Introduction to Large Lang"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC302H1",
        "title": "Engineering Large Software Systems",
        "units": 0.5
      },
      "nus_course": {
        "code": "CS3213",
        "title": "Software Requirements Sp"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC384H1",
        "title": "Introduction to Artificial Intelligence",
        "units": 0.5
      },
      "nus_course": {
        "code": "CS3263",
        "title": "Foundations of Artificial In"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC3465H1",
        "title": "Formal Methods in Software Design",
        "units": 0.5
      },
      "nus_course": {
        "code": "CS4211",
        "title": "Formal Methods for Softwa"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC369H1",
        "title": "Operating Systems",
        "units": 0.5
      },
      "nus_course": {
        "code": "CS2106",
        "title": "Introduction to Operating"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "ECO375H1",
        "title": "Foundations of Econometrics",
        "units": 0.5
      },
      "nus_course": {
        "code": "BT2101",
        "title": "Econometrics Modeling for"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "BCB420H1",
        "title": "Computational Systems Biology",
        "units": 0.5
      },
      "nus_course": {
        "code": "CS4220",
        "title": "Knowledge Discovery Meth"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "ECE352",
        "title": "Computer Organization",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS2100",
        "title": "Computer Organisation"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "ECE358",
        "title": "Foundations of Computing",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS3230",
        "title": "Design and Analysis of Alg"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC322H5",
        "title": "Introduction to Algebraic Cryptography",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS4236",
        "title": "Cryptography in Practice:"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC358H1",
        "title": "Principles of Computer Networks",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS2105",
        "title": "Introduction to Computer"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "ECE568H1",
        "title": "Computer Security",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS3235",
        "title": "Computer Security"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC311H1",
        "title": "Introduction to Machine Learning",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS3244",
        "title": "Machine Learning"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC410",
        "title": "Software Verification and Testing",
        "units": 0.5
      },
      "nus_course": {
        "code": "CS4218",
        "title": "Software Testing"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC488",
        "title": "Compilers and Interpreters",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS4212",
        "title": "Compiler Design"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC469",
        "title": "Operating Systems Design and Implementation",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS3221",
        "title": "Operating Systems Design"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC367H1",
        "title": "Parallel Programming",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS3210",
        "title": "Parallel Computing"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "MIE369H1",
        "title": "Introduction to Artificial Intelligence",
        "units": 0.5
      },
      "nus_course": {
        "code": "CS3243",
        "title": "Introduction to Artificial In"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "ROB311H1",
        "title": "Artificial Intellgence",
        "units": 0.5
      },
      "nus_course": {
        "code": "CS3243",
        "title": "Introduction to Artificial In"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "RSM434",
        "title": "Financial Trading Strategies",
        "units": 0.5
      },
      "nus_course": {
        "code": "IS4226",
        "title": "Systematic Trading Strate"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "ACT350",
        "title": "Applied Probability for Actuarial Science",
        "units": 0.5
      },
      "nus_course": {
        "code": "BT3102",
        "title": "Computational Methods fo"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC373H1",
        "title": "Algorithm Design, Analysis & Complexity",
        "units": 0.5
      },
      "nus_course": {
        "code": "CS3230",
        "title": "Design and Analysis of Alg"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC384H1",
        "title": "Introduction to Artificial Intelligence",
        "units": 0.5
      },
      "nus_course": {
        "code": "CS3243",
        "title": "Introduction to Artificial In"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC343H1",
        "title": "Introduction to Databases",
        "units": 0.5
      },
      "nus_course": {
        "code": "CS2102",
        "title": "Database Systems"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC324H1",
        "title": "Principles of Programming Languages",
        "units": 0.5
      },
      "nus_course": {
        "code": "CS2104",
        "title": "Programming Language C"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC373H",
        "title": "Algorithm Design and Analysis",
        "units": 0.5
      },
      "nus_course": {
        "code": "CS3230",
        "title": "Design and Analysis of Alg"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC317H1",
        "title": "Computer Graphics",
        "units": 0.5
      },
      "nus_course": {
        "code": "CS3241",
        "title": "Computer Graphics"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC485H1",
        "title": "Computational Linguistics",
        "units": 0.5
      },
      "nus_course": {
        "code": "CS4248",
        "title": "Introduction to Large Lang"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "APS360H1",
        "title": "Applied Fundamentals of Deep Learning",
        "units": 0.5
      },
      "nus_course": {
        "code": "BT4240",
        "title": "Machine Learning for Pred"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC465",
        "title": "Formal Methods in Software Design",
        "units": 0.5
      },
      "nus_course": {
        "code": "CS4211",
        "title": "Formal Methods for Softwa"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC457H1",
        "title": "Principles of Computer Networks",
        "units": 0.5
      },
      "nus_course": {
        "code": "CS2105",
        "title": "Introduction to Computer"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC301H1",
        "title": "Introduction to Software Engineering",
        "units": 0.5
      },
      "nus_course": {
        "code": "CS2103",
        "title": "Software Engineering"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC411H1",
        "title": "Machine Learning and Data Mining",
        "units": 0.5
      },
      "nus_course": {
        "code": "CS3244",
        "title": "Machine Learning"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "ECE421",
        "title": "Introduction to Machine Learning",
        "units": 0.5
      },
      "nus_course": {
        "code": "CS3244",
        "title": "Machine Learning"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "ROB311",
        "title": "Artificial Intelligence",
        "units": 0.5
      },
      "nus_course": {
        "code": "CS3243",
        "title": "Introduction to Artificial In"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "ECE521",
        "title": "Inference Algorithms and Machine Learning",
        "units": 0.5
      },
      "nus_course": {
        "code": "CS3244",
        "title": "Machine Learning"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSC207H1",
        "title": "Software Design",
        "units": 0.5
      },
      "nus_course": {
        "code": "Software Engineering",
        "title": null
      },
      "faculty": "School of Computing",
      "source_page": 2
    },
    {
      "partner_course": {
        "code": "CSC165H1",
        "title": "Mathematical Expression and Reasoning for Computer Science",
        "units": 0.5
      },
      "nus_course": {
        "code": "Discrete Structures",
        "title": null
      },
      "faculty": "School of Computing",
      "source_page": 2
    },
    {
      "partner_course": {
        "code": "CSCC11H3",
        "title": "Introduction to Machine Learning and Data Mining",
        "units": 0.5
      },
      "nus_course": {
        "code": "Foundations of Machine Le",
        "title": null
      },
      "faculty": "School of Computing",
      "source_page": 2
    },
    {
      "partner_course": {
        "code": "MSE403H1",
        "title": "Data Sciences and Analytics for Materials Engineers",
        "units": 0.5
      },
      "nus_course": {
        "code": "Machine Learning for Pred",
        "title": null
      },
      "faculty": "School of Computing",
      "source_page": 2
    },
    {
      "partner_course": {
        "code": "CSC343H1",
        "title": "Introduction to Databases",
        "units": 0.5
      },
      "nus_course": {
        "code": "Database Technology and",
        "title": null
      },
      "faculty": "School of Computing",
      "source_page": 2
    },
    {
      "partner_course": {
        "code": "108H1F",
        "title": "Introduction to Computer Programming",
        "units": 0.5
      },
      "nus_course": {
        "code": "Programming Methodology",
        "title": null
      },
      "faculty": "School of Computing",
      "source_page": 2
    },
    {
      "partner_course": {
        "code": "ECE243H1",
        "title": "Computer Organization",
        "units": 0.5
      },
      "nus_course": {
        "code": "Computer Organisation",
        "title": null
      },
      "faculty": "School of Computing",
      "source_page": 2
    }
  ]
}
', '{"source": {"file": "toronto.pdf", "system": "NUS EduRec Course Mappings Search", "retrieved_at": "2026-10-14"}, "mappings": [{"faculty": "School of Computing", "nus_course": {"code": "CS2106", "title": "Introduction to Operating"}, "source_page": 1, "partner_course": {"code": "ECE344H1", "title": "Operating Systems", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "CS2103", "title": "Software Engineering"}, "source_page": 1, "partner_course": {"code": "CSC444H1", "title": "Software Engineering", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "CS2104", "title": "Programming Language C"}, "source_page": 1, "partner_course": {"code": "CSC326H1", "title": "Programming Languages", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3247", "title": "Game Development"}, "source_page": 1, "partner_course": {"code": "CSC404H1", "title": "Introduction to Video Game Design", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3244", "title": "Machine Learning"}, "source_page": 1, "partner_course": {"code": "ROB313H1", "title": "Introduction to Learning from Data", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "CS4249", "title": "Quantitative Methods of H"}, "source_page": 1, "partner_course": {"code": "CSC428H1-S", "title": "Human-Computer Interaction", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "CS4243", "title": "Computer Vision and Patte"}, "source_page": 1, "partner_course": {"code": "CSC420H1", "title": "Introduction to Image Understanding", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "CS5242", "title": "Neural Networks and Deep"}, "source_page": 1, "partner_course": {"code": "CSC413H1", "title": "\" Neural Networks and Deep Learning\"", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "BT3103", "title": "Application Systems Deve"}, "source_page": 1, "partner_course": {"code": "CSC309H1", "title": "Programming on the Web", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "BT3102", "title": "Computational Methods fo"}, "source_page": 1, "partner_course": {"code": "CSC412", "title": "Probabilistic Learning and Reasoning", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "IS3107", "title": "Data Engineering"}, "source_page": 1, "partner_course": {"code": "CSC443H1", "title": "Database System Technology", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3264", "title": "Foundations of Machine Le"}, "source_page": 1, "partner_course": {"code": "CSC311H1", "title": "Introduction to Machine Learning", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "CS4248", "title": "Introduction to Large Lang"}, "source_page": 1, "partner_course": {"code": "CSC401H1", "title": "Natural Language Computing", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3213", "title": "Software Requirements Sp"}, "source_page": 1, "partner_course": {"code": "CSC302H1", "title": "Engineering Large Software Systems", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3263", "title": "Foundations of Artificial In"}, "source_page": 1, "partner_course": {"code": "CSC384H1", "title": "Introduction to Artificial Intelligence", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "CS4211", "title": "Formal Methods for Softwa"}, "source_page": 1, "partner_course": {"code": "CSC3465H1", "title": "Formal Methods in Software Design", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "CS2106", "title": "Introduction to Operating"}, "source_page": 1, "partner_course": {"code": "CSC369H1", "title": "Operating Systems", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "BT2101", "title": "Econometrics Modeling for"}, "source_page": 1, "partner_course": {"code": "ECO375H1", "title": "Foundations of Econometrics", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "CS4220", "title": "Knowledge Discovery Meth"}, "source_page": 1, "partner_course": {"code": "BCB420H1", "title": "Computational Systems Biology", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "CS2100", "title": "Computer Organisation"}, "source_page": 1, "partner_course": {"code": "ECE352", "title": "Computer Organization", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3230", "title": "Design and Analysis of Alg"}, "source_page": 1, "partner_course": {"code": "ECE358", "title": "Foundations of Computing", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS4236", "title": "Cryptography in Practice:"}, "source_page": 1, "partner_course": {"code": "CSC322H5", "title": "Introduction to Algebraic Cryptography", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS2105", "title": "Introduction to Computer"}, "source_page": 1, "partner_course": {"code": "CSC358H1", "title": "Principles of Computer Networks", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3235", "title": "Computer Security"}, "source_page": 1, "partner_course": {"code": "ECE568H1", "title": "Computer Security", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3244", "title": "Machine Learning"}, "source_page": 1, "partner_course": {"code": "CSC311H1", "title": "Introduction to Machine Learning", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS4218", "title": "Software Testing"}, "source_page": 1, "partner_course": {"code": "CSC410", "title": "Software Verification and Testing", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "CS4212", "title": "Compiler Design"}, "source_page": 1, "partner_course": {"code": "CSC488", "title": "Compilers and Interpreters", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3221", "title": "Operating Systems Design"}, "source_page": 1, "partner_course": {"code": "CSC469", "title": "Operating Systems Design and Implementation", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3210", "title": "Parallel Computing"}, "source_page": 1, "partner_course": {"code": "CSC367H1", "title": "Parallel Programming", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3243", "title": "Introduction to Artificial In"}, "source_page": 1, "partner_course": {"code": "MIE369H1", "title": "Introduction to Artificial Intelligence", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3243", "title": "Introduction to Artificial In"}, "source_page": 1, "partner_course": {"code": "ROB311H1", "title": "Artificial Intellgence", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "IS4226", "title": "Systematic Trading Strate"}, "source_page": 1, "partner_course": {"code": "RSM434", "title": "Financial Trading Strategies", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "BT3102", "title": "Computational Methods fo"}, "source_page": 1, "partner_course": {"code": "ACT350", "title": "Applied Probability for Actuarial Science", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3230", "title": "Design and Analysis of Alg"}, "source_page": 1, "partner_course": {"code": "CSC373H1", "title": "Algorithm Design, Analysis & Complexity", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3243", "title": "Introduction to Artificial In"}, "source_page": 1, "partner_course": {"code": "CSC384H1", "title": "Introduction to Artificial Intelligence", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "CS2102", "title": "Database Systems"}, "source_page": 1, "partner_course": {"code": "CSC343H1", "title": "Introduction to Databases", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "CS2104", "title": "Programming Language C"}, "source_page": 1, "partner_course": {"code": "CSC324H1", "title": "Principles of Programming Languages", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3230", "title": "Design and Analysis of Alg"}, "source_page": 1, "partner_course": {"code": "CSC373H", "title": "Algorithm Design and Analysis", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3241", "title": "Computer Graphics"}, "source_page": 1, "partner_course": {"code": "CSC317H1", "title": "Computer Graphics", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "CS4248", "title": "Introduction to Large Lang"}, "source_page": 1, "partner_course": {"code": "CSC485H1", "title": "Computational Linguistics", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "BT4240", "title": "Machine Learning for Pred"}, "source_page": 1, "partner_course": {"code": "APS360H1", "title": "Applied Fundamentals of Deep Learning", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "CS4211", "title": "Formal Methods for Softwa"}, "source_page": 1, "partner_course": {"code": "CSC465", "title": "Formal Methods in Software Design", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "CS2105", "title": "Introduction to Computer"}, "source_page": 1, "partner_course": {"code": "CSC457H1", "title": "Principles of Computer Networks", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "CS2103", "title": "Software Engineering"}, "source_page": 1, "partner_course": {"code": "CSC301H1", "title": "Introduction to Software Engineering", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3244", "title": "Machine Learning"}, "source_page": 1, "partner_course": {"code": "CSC411H1", "title": "Machine Learning and Data Mining", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3244", "title": "Machine Learning"}, "source_page": 1, "partner_course": {"code": "ECE421", "title": "Introduction to Machine Learning", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3243", "title": "Introduction to Artificial In"}, "source_page": 1, "partner_course": {"code": "ROB311", "title": "Artificial Intelligence", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3244", "title": "Machine Learning"}, "source_page": 1, "partner_course": {"code": "ECE521", "title": "Inference Algorithms and Machine Learning", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "Software Engineering", "title": null}, "source_page": 2, "partner_course": {"code": "CSC207H1", "title": "Software Design", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "Discrete Structures", "title": null}, "source_page": 2, "partner_course": {"code": "CSC165H1", "title": "Mathematical Expression and Reasoning for Computer Science", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "Foundations of Machine Le", "title": null}, "source_page": 2, "partner_course": {"code": "CSCC11H3", "title": "Introduction to Machine Learning and Data Mining", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "Machine Learning for Pred", "title": null}, "source_page": 2, "partner_course": {"code": "MSE403H1", "title": "Data Sciences and Analytics for Materials Engineers", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "Database Technology and", "title": null}, "source_page": 2, "partner_course": {"code": "CSC343H1", "title": "Introduction to Databases", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "Programming Methodology", "title": null}, "source_page": 2, "partner_course": {"code": "108H1F", "title": "Introduction to Computer Programming", "units": 0.5}}, {"faculty": "School of Computing", "nus_course": {"code": "Computer Organisation", "title": null}, "source_page": 2, "partner_course": {"code": "ECE243H1", "title": "Computer Organization", "units": 0.5}}], "mapping_count": 55, "partner_university": {"name": "University of Toronto", "edurec_id": "E0000000684"}}', 'ad1baec1ee241b7b2ba253a65874615f66471abb384bf93a3fb66fc1430ddef9', 17338, '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_snapshots (id, batch_id, file_path, source_kind, raw_text, parsed_json, sha256, byte_size, archived_at) OVERRIDING SYSTEM VALUE VALUES (5, 1, 'data/mapping/japan/kyoto.json', 'mapping', '{
  "partner_university": {
    "name": "Kyoto University",
    "edurec_id": "E0000000326"
  },
  "source": {
    "file": "kyoto.pdf",
    "system": "NUS EduRec Course Mappings Search",
    "retrieved_at": "2026-10-14"
  },
  "mapping_count": 7,
  "mappings": [
    {
      "partner_course": {
        "code": "ENG39098",
        "title": "Databases",
        "units": 2.0
      },
      "nus_course": {
        "code": "CS2102",
        "title": "Database Systems"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "ENG39116",
        "title": "Artificial Intelligence",
        "units": 2.0
      },
      "nus_course": {
        "code": "CS3243",
        "title": "Introduction to Artificial In"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "ENG39128",
        "title": "Implementation of Programming Languages",
        "units": 2.0
      },
      "nus_course": {
        "code": "CS4215",
        "title": "Programming Language Im"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "T019001",
        "title": "Information Network-E2",
        "units": 2.0
      },
      "nus_course": {
        "code": "CS2105",
        "title": "Introduction to Computer"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "T057001",
        "title": "Fundamentals of Artificial Intelligence- E2",
        "units": 2.0
      },
      "nus_course": {
        "code": "CS3244",
        "title": "Machine Learning"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "T57002",
        "title": "Fundamentals of Artificial Intelligence- E2",
        "units": 2.0
      },
      "nus_course": {
        "code": "CS2109S",
        "title": "Introduction to AI and Mac"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "U-LAS30 20044 LE10",
        "title": "Introduction to Formal Languages-E2",
        "units": 2.0
      },
      "nus_course": {
        "code": "CS3231",
        "title": "Theory of Computation"
      },
      "faculty": "School of Computing",
      "source_page": 1
    }
  ]
}
', '{"source": {"file": "kyoto.pdf", "system": "NUS EduRec Course Mappings Search", "retrieved_at": "2026-10-14"}, "mappings": [{"faculty": "School of Computing", "nus_course": {"code": "CS2102", "title": "Database Systems"}, "source_page": 1, "partner_course": {"code": "ENG39098", "title": "Databases", "units": 2.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3243", "title": "Introduction to Artificial In"}, "source_page": 1, "partner_course": {"code": "ENG39116", "title": "Artificial Intelligence", "units": 2.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS4215", "title": "Programming Language Im"}, "source_page": 1, "partner_course": {"code": "ENG39128", "title": "Implementation of Programming Languages", "units": 2.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS2105", "title": "Introduction to Computer"}, "source_page": 1, "partner_course": {"code": "T019001", "title": "Information Network-E2", "units": 2.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3244", "title": "Machine Learning"}, "source_page": 1, "partner_course": {"code": "T057001", "title": "Fundamentals of Artificial Intelligence- E2", "units": 2.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS2109S", "title": "Introduction to AI and Mac"}, "source_page": 1, "partner_course": {"code": "T57002", "title": "Fundamentals of Artificial Intelligence- E2", "units": 2.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3231", "title": "Theory of Computation"}, "source_page": 1, "partner_course": {"code": "U-LAS30 20044 LE10", "title": "Introduction to Formal Languages-E2", "units": 2.0}}], "mapping_count": 7, "partner_university": {"name": "Kyoto University", "edurec_id": "E0000000326"}}', 'a42cb28be8372df929cd3c79b9860922ef15464758557689801ea004fdd48cd3', 2449, '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_snapshots (id, batch_id, file_path, source_kind, raw_text, parsed_json, sha256, byte_size, archived_at) OVERRIDING SYSTEM VALUE VALUES (6, 1, 'data/mapping/korea/korea.json', 'mapping', '{
  "partner_university": {
    "name": "Korea University",
    "edurec_id": "E0000000544"
  },
  "source": {
    "file": "korea.pdf",
    "system": "NUS EduRec Course Mappings Search",
    "retrieved_at": "2026-10-14"
  },
  "mapping_count": 36,
  "mappings": [
    {
      "partner_course": {
        "code": "COSE101",
        "title": "Computer Programming I",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS1010E",
        "title": "Programming Methodology"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "BUSS 216",
        "title": "Business Analytics I (English)",
        "units": 3.0
      },
      "nus_course": {
        "code": "BT1101",
        "title": "Introduction to Business A"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "COSE211",
        "title": "Discrete Mathematics",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS1231",
        "title": "Discrete Structures"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "COSE 342",
        "title": "Computer Network",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS2105",
        "title": "Introduction to Computer"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "COSE 362",
        "title": "Machine Learning",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS3244",
        "title": "Machine Learning"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "KECE443",
        "title": "Object-Oriented Programming and Laboratory",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS2030",
        "title": "Programming Methodology"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "COSE 213",
        "title": "Data Structures",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS2040C",
        "title": "Data Structures and Algor"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "COSE341",
        "title": "Operating Systems",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS2106",
        "title": "Introduction to Operating"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "COSE361",
        "title": "Artificial Intelligence (English)",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS3243",
        "title": "Introduction to Artificial In"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "COSE371",
        "title": "Databases",
        "units": 3.0
      },
      "nus_course": {
        "code": "IT2002",
        "title": "Database Technology and"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "COSE474",
        "title": "Deep Learning",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS5242",
        "title": "Neural Networks and Deep"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "KECE345",
        "title": "\" MACHINE LEARNING AND INTELLIGENCE FOR ELECTRICAL ENGINEERS(English)\"",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS3244",
        "title": "Machine Learning"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "BUSS217",
        "title": "Business Analytics II",
        "units": 3.0
      },
      "nus_course": {
        "code": "BT4240",
        "title": "Machine Learning for Pred"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "KECE421",
        "title": "INFORMATION AND CODING THEORY",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS3236",
        "title": "Introduction to Informatio"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "COSE214",
        "title": "ALORITHMS",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS3230",
        "title": "Design and Analysis of Alg"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "BUSS475",
        "title": "Internet Marketing",
        "units": 3.0
      },
      "nus_course": {
        "code": "IS3150",
        "title": "Digital Media Marketing"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "COSE389",
        "title": "ENTREPRENEURSHIP & LEADERSHIP",
        "units": 3.0
      },
      "nus_course": {
        "code": "IS3103",
        "title": "Digital Transformation and"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "COSE461",
        "title": "NATURAL LANGUAGE PROCESSING",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS4248",
        "title": "Introduction to Large Lang"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "COSE215",
        "title": "THEORY OF COMPUTATION",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS3231",
        "title": "Theory of Computation"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "COSE331",
        "title": "COMPUTER GRAPHICS",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS3241",
        "title": "Computer Graphics"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "COSE212",
        "title": "PROGRAMMING LANGUAGES",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS2104",
        "title": "Programming Language C"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "BNCS411",
        "title": "INTRODUCTION TO BRAIN AND MACHINE LEARNING",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS3244",
        "title": "Machine Learning"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "BUSS316",
        "title": "Operations Analytics (English)",
        "units": 3.0
      },
      "nus_course": {
        "code": "BT4240",
        "title": "Machine Learning for Pred"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "SMRT336",
        "title": "AI Security II (English)",
        "units": 3.0
      },
      "nus_course": {
        "code": "IS4246",
        "title": "Smart Systems and AI Go"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "STAT346",
        "title": "Statistical Data Science I (English)\"",
        "units": 3.0
      },
      "nus_course": {
        "code": "BT4221",
        "title": "Advanced Analytics with B"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "BUSS305",
        "title": "Artificial Intelligence for Business (English)\"",
        "units": 3.0
      },
      "nus_course": {
        "code": "IS4246",
        "title": "Smart Systems and AI Go"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "KHPM410",
        "title": "Data Science in Healthcare",
        "units": 3.0
      },
      "nus_course": {
        "code": "BT4222",
        "title": "Mining Web Data for Busin"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "COSE432",
        "title": "HUMAN COMPUTER INTERACTION",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS3240",
        "title": "Interaction Design"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "COSE342",
        "title": "Computer Network",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS2105",
        "title": "Introduction to Computer"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "BUSS317",
        "title": "Social Media Analytics",
        "units": 3.0
      },
      "nus_course": {
        "code": "BT4222",
        "title": "Mining Web Data for Busin"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "BUSS410",
        "title": "Technological Innovation Management: A Pre-requisite for Successful Entrepreneurship",
        "units": 3.0
      },
      "nus_course": {
        "code": "IS4261",
        "title": "Designing AI-driven Busin"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "COSE442",
        "title": "Wireless Communications",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS4222",
        "title": "Wireless Networking"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "COSE436",
        "title": "Interactive Visualization",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS3241",
        "title": "Computer Graphics"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "KECE470",
        "title": "Pattern Recognition",
        "units": 3.0
      },
      "nus_course": {
        "code": "BT4240",
        "title": "Machine Learning for Pred"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "BUSS215",
        "title": "INTRODUCTION TO MANAGEMENT INFORMATION SYSTEMS(English)",
        "units": 3.0
      },
      "nus_course": {
        "code": "IS3103",
        "title": "Digital Transformation and"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "BUSS317",
        "title": "Social Media Analytics",
        "units": 3.0
      },
      "nus_course": {
        "code": "IS4241",
        "title": "Social Media Network Ana"
      },
      "faculty": "School of Computing",
      "source_page": 1
    }
  ]
}
', '{"source": {"file": "korea.pdf", "system": "NUS EduRec Course Mappings Search", "retrieved_at": "2026-10-14"}, "mappings": [{"faculty": "School of Computing", "nus_course": {"code": "CS1010E", "title": "Programming Methodology"}, "source_page": 1, "partner_course": {"code": "COSE101", "title": "Computer Programming I", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "BT1101", "title": "Introduction to Business A"}, "source_page": 1, "partner_course": {"code": "BUSS 216", "title": "Business Analytics I (English)", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS1231", "title": "Discrete Structures"}, "source_page": 1, "partner_course": {"code": "COSE211", "title": "Discrete Mathematics", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS2105", "title": "Introduction to Computer"}, "source_page": 1, "partner_course": {"code": "COSE 342", "title": "Computer Network", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3244", "title": "Machine Learning"}, "source_page": 1, "partner_course": {"code": "COSE 362", "title": "Machine Learning", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS2030", "title": "Programming Methodology"}, "source_page": 1, "partner_course": {"code": "KECE443", "title": "Object-Oriented Programming and Laboratory", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS2040C", "title": "Data Structures and Algor"}, "source_page": 1, "partner_course": {"code": "COSE 213", "title": "Data Structures", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS2106", "title": "Introduction to Operating"}, "source_page": 1, "partner_course": {"code": "COSE341", "title": "Operating Systems", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3243", "title": "Introduction to Artificial In"}, "source_page": 1, "partner_course": {"code": "COSE361", "title": "Artificial Intelligence (English)", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "IT2002", "title": "Database Technology and"}, "source_page": 1, "partner_course": {"code": "COSE371", "title": "Databases", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS5242", "title": "Neural Networks and Deep"}, "source_page": 1, "partner_course": {"code": "COSE474", "title": "Deep Learning", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3244", "title": "Machine Learning"}, "source_page": 1, "partner_course": {"code": "KECE345", "title": "\" MACHINE LEARNING AND INTELLIGENCE FOR ELECTRICAL ENGINEERS(English)\"", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "BT4240", "title": "Machine Learning for Pred"}, "source_page": 1, "partner_course": {"code": "BUSS217", "title": "Business Analytics II", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3236", "title": "Introduction to Informatio"}, "source_page": 1, "partner_course": {"code": "KECE421", "title": "INFORMATION AND CODING THEORY", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3230", "title": "Design and Analysis of Alg"}, "source_page": 1, "partner_course": {"code": "COSE214", "title": "ALORITHMS", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "IS3150", "title": "Digital Media Marketing"}, "source_page": 1, "partner_course": {"code": "BUSS475", "title": "Internet Marketing", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "IS3103", "title": "Digital Transformation and"}, "source_page": 1, "partner_course": {"code": "COSE389", "title": "ENTREPRENEURSHIP & LEADERSHIP", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS4248", "title": "Introduction to Large Lang"}, "source_page": 1, "partner_course": {"code": "COSE461", "title": "NATURAL LANGUAGE PROCESSING", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3231", "title": "Theory of Computation"}, "source_page": 1, "partner_course": {"code": "COSE215", "title": "THEORY OF COMPUTATION", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3241", "title": "Computer Graphics"}, "source_page": 1, "partner_course": {"code": "COSE331", "title": "COMPUTER GRAPHICS", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS2104", "title": "Programming Language C"}, "source_page": 1, "partner_course": {"code": "COSE212", "title": "PROGRAMMING LANGUAGES", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3244", "title": "Machine Learning"}, "source_page": 1, "partner_course": {"code": "BNCS411", "title": "INTRODUCTION TO BRAIN AND MACHINE LEARNING", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "BT4240", "title": "Machine Learning for Pred"}, "source_page": 1, "partner_course": {"code": "BUSS316", "title": "Operations Analytics (English)", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "IS4246", "title": "Smart Systems and AI Go"}, "source_page": 1, "partner_course": {"code": "SMRT336", "title": "AI Security II (English)", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "BT4221", "title": "Advanced Analytics with B"}, "source_page": 1, "partner_course": {"code": "STAT346", "title": "Statistical Data Science I (English)\"", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "IS4246", "title": "Smart Systems and AI Go"}, "source_page": 1, "partner_course": {"code": "BUSS305", "title": "Artificial Intelligence for Business (English)\"", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "BT4222", "title": "Mining Web Data for Busin"}, "source_page": 1, "partner_course": {"code": "KHPM410", "title": "Data Science in Healthcare", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3240", "title": "Interaction Design"}, "source_page": 1, "partner_course": {"code": "COSE432", "title": "HUMAN COMPUTER INTERACTION", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS2105", "title": "Introduction to Computer"}, "source_page": 1, "partner_course": {"code": "COSE342", "title": "Computer Network", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "BT4222", "title": "Mining Web Data for Busin"}, "source_page": 1, "partner_course": {"code": "BUSS317", "title": "Social Media Analytics", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "IS4261", "title": "Designing AI-driven Busin"}, "source_page": 1, "partner_course": {"code": "BUSS410", "title": "Technological Innovation Management: A Pre-requisite for Successful Entrepreneurship", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS4222", "title": "Wireless Networking"}, "source_page": 1, "partner_course": {"code": "COSE442", "title": "Wireless Communications", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3241", "title": "Computer Graphics"}, "source_page": 1, "partner_course": {"code": "COSE436", "title": "Interactive Visualization", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "BT4240", "title": "Machine Learning for Pred"}, "source_page": 1, "partner_course": {"code": "KECE470", "title": "Pattern Recognition", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "IS3103", "title": "Digital Transformation and"}, "source_page": 1, "partner_course": {"code": "BUSS215", "title": "INTRODUCTION TO MANAGEMENT INFORMATION SYSTEMS(English)", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "IS4241", "title": "Social Media Network Ana"}, "source_page": 1, "partner_course": {"code": "BUSS317", "title": "Social Media Analytics", "units": 3.0}}], "mapping_count": 36, "partner_university": {"name": "Korea University", "edurec_id": "E0000000544"}}', '96cdd005ff1d79923e7d3d19025bad6565f9a58dcf6dd6da16046e929b3a5946', 11348, '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_snapshots (id, batch_id, file_path, source_kind, raw_text, parsed_json, sha256, byte_size, archived_at) OVERRIDING SYSTEM VALUE VALUES (7, 1, 'data/mapping/korea/yonsei.json', 'mapping', '{
  "partner_university": {
    "name": "Yonsei University",
    "edurec_id": "E0000000548"
  },
  "source": {
    "file": "yonsei.pdf",
    "system": "NUS EduRec Course Mappings Search",
    "retrieved_at": "2026-10-14"
  },
  "mapping_count": 24,
  "mappings": [
    {
      "partner_course": {
        "code": "CSI4120",
        "title": "MACHINE LEARNING",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS3244",
        "title": "Machine Learning"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "AIC2120",
        "title": "INTRODUCTION TO AI AND ITS APPLICATIONS",
        "units": 3.0
      },
      "nus_course": {
        "code": "IT1244",
        "title": "Artificial Intelligence: Tech"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSI4116",
        "title": "Computer Vision",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS4243",
        "title": "Computer Vision and Patte"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "MAT2106",
        "title": "DISCRETE MATHEMATICS",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS1231",
        "title": "Discrete Structures"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSI4108",
        "title": "Artificial Intelligence",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS3243",
        "title": "Introduction to Artificial In"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CAS3116",
        "title": "COMPUTER VISION",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS4243",
        "title": "Computer Vision and Patte"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "STA4123",
        "title": "INTRODUCTION TO OPTIMIZATION FOR DATA SCIENCE",
        "units": 3.0
      },
      "nus_course": {
        "code": "BT3104",
        "title": "Optimization Methods for"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CAS3120-01",
        "title": "MACHINE LEARNING",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS3244",
        "title": "Machine Learning"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSI3109",
        "title": "AUTOMATA AND FORMAL LANGUAGES",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS3231",
        "title": "Theory of Computation"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "BIZ3189-04",
        "title": "MANAGEMENT INFORMATION SYSTEMS",
        "units": 3.0
      },
      "nus_course": {
        "code": "IS3103",
        "title": "Digital Transformation and"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "EEE7501",
        "title": "NEURAL NETWORK",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS5242",
        "title": "Neural Networks and Deep"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "ISM6011",
        "title": "Global IT Management",
        "units": 3.0
      },
      "nus_course": {
        "code": "IS3103",
        "title": "Digital Transformation and"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSI4106",
        "title": "Computer Networks",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS2105",
        "title": "Introduction to Computer"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "EEE3450",
        "title": "COMMUNICATION NETWORKS",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS2105",
        "title": "Introduction to Computer"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "EEE3314",
        "title": "INTRODUCTION ARTIFICIAL INTELLIGENCE",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS3244",
        "title": "Machine Learning"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "STA3141",
        "title": "MATHEMATICS FOR MACHINE LEARNING",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS3244",
        "title": "Machine Learning"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "STA3142",
        "title": "STATISTICAL MACHINE LEARNING",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS3244",
        "title": "Machine Learning"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "EE4624",
        "title": "WIRELESS AND MOBILE NETWORKS",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS4222",
        "title": "Wireless Networking"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "EEE3314",
        "title": "INTRODUCTION ARTIFICIAL INTELLIGENCE",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS3263",
        "title": "Foundations of Artificial In"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "PHY4125",
        "title": "QUANTUM COMPUTER",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS4268",
        "title": "Quantum Computing"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSI2103",
        "title": "Data Structures",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS2040",
        "title": "Data Structures and Algor"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "CSI4109",
        "title": "Information Security",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS2107",
        "title": "Introduction to Informatio"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "STA3142",
        "title": "STATISTICAL MACHINE LEARNING",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS3264",
        "title": "Foundations of Machine Le"
      },
      "faculty": "School of Computing",
      "source_page": 1
    },
    {
      "partner_course": {
        "code": "STA9131",
        "title": "DEEP LEARNING FOR VISUAL RECOGNITION",
        "units": 3.0
      },
      "nus_course": {
        "code": "CS5242",
        "title": "Neural Networks and Deep"
      },
      "faculty": "School of Computing",
      "source_page": 1
    }
  ]
}
', '{"source": {"file": "yonsei.pdf", "system": "NUS EduRec Course Mappings Search", "retrieved_at": "2026-10-14"}, "mappings": [{"faculty": "School of Computing", "nus_course": {"code": "CS3244", "title": "Machine Learning"}, "source_page": 1, "partner_course": {"code": "CSI4120", "title": "MACHINE LEARNING", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "IT1244", "title": "Artificial Intelligence: Tech"}, "source_page": 1, "partner_course": {"code": "AIC2120", "title": "INTRODUCTION TO AI AND ITS APPLICATIONS", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS4243", "title": "Computer Vision and Patte"}, "source_page": 1, "partner_course": {"code": "CSI4116", "title": "Computer Vision", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS1231", "title": "Discrete Structures"}, "source_page": 1, "partner_course": {"code": "MAT2106", "title": "DISCRETE MATHEMATICS", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3243", "title": "Introduction to Artificial In"}, "source_page": 1, "partner_course": {"code": "CSI4108", "title": "Artificial Intelligence", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS4243", "title": "Computer Vision and Patte"}, "source_page": 1, "partner_course": {"code": "CAS3116", "title": "COMPUTER VISION", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "BT3104", "title": "Optimization Methods for"}, "source_page": 1, "partner_course": {"code": "STA4123", "title": "INTRODUCTION TO OPTIMIZATION FOR DATA SCIENCE", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3244", "title": "Machine Learning"}, "source_page": 1, "partner_course": {"code": "CAS3120-01", "title": "MACHINE LEARNING", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3231", "title": "Theory of Computation"}, "source_page": 1, "partner_course": {"code": "CSI3109", "title": "AUTOMATA AND FORMAL LANGUAGES", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "IS3103", "title": "Digital Transformation and"}, "source_page": 1, "partner_course": {"code": "BIZ3189-04", "title": "MANAGEMENT INFORMATION SYSTEMS", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS5242", "title": "Neural Networks and Deep"}, "source_page": 1, "partner_course": {"code": "EEE7501", "title": "NEURAL NETWORK", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "IS3103", "title": "Digital Transformation and"}, "source_page": 1, "partner_course": {"code": "ISM6011", "title": "Global IT Management", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS2105", "title": "Introduction to Computer"}, "source_page": 1, "partner_course": {"code": "CSI4106", "title": "Computer Networks", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS2105", "title": "Introduction to Computer"}, "source_page": 1, "partner_course": {"code": "EEE3450", "title": "COMMUNICATION NETWORKS", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3244", "title": "Machine Learning"}, "source_page": 1, "partner_course": {"code": "EEE3314", "title": "INTRODUCTION ARTIFICIAL INTELLIGENCE", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3244", "title": "Machine Learning"}, "source_page": 1, "partner_course": {"code": "STA3141", "title": "MATHEMATICS FOR MACHINE LEARNING", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3244", "title": "Machine Learning"}, "source_page": 1, "partner_course": {"code": "STA3142", "title": "STATISTICAL MACHINE LEARNING", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS4222", "title": "Wireless Networking"}, "source_page": 1, "partner_course": {"code": "EE4624", "title": "WIRELESS AND MOBILE NETWORKS", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3263", "title": "Foundations of Artificial In"}, "source_page": 1, "partner_course": {"code": "EEE3314", "title": "INTRODUCTION ARTIFICIAL INTELLIGENCE", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS4268", "title": "Quantum Computing"}, "source_page": 1, "partner_course": {"code": "PHY4125", "title": "QUANTUM COMPUTER", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS2040", "title": "Data Structures and Algor"}, "source_page": 1, "partner_course": {"code": "CSI2103", "title": "Data Structures", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS2107", "title": "Introduction to Informatio"}, "source_page": 1, "partner_course": {"code": "CSI4109", "title": "Information Security", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS3264", "title": "Foundations of Machine Le"}, "source_page": 1, "partner_course": {"code": "STA3142", "title": "STATISTICAL MACHINE LEARNING", "units": 3.0}}, {"faculty": "School of Computing", "nus_course": {"code": "CS5242", "title": "Neural Networks and Deep"}, "source_page": 1, "partner_course": {"code": "STA9131", "title": "DEEP LEARNING FOR VISUAL RECOGNITION", "units": 3.0}}], "mapping_count": 24, "partner_university": {"name": "Yonsei University", "edurec_id": "E0000000548"}}', 'fd4b3635fa899f2e27c1a28592bf5c50f2908fe0992608d26d86a0c5ca269634', 7579, '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_snapshots (id, batch_id, file_path, source_kind, raw_text, parsed_json, sha256, byte_size, archived_at) OVERRIDING SYSTEM VALUE VALUES (8, 1, 'data/repairs/catalog_repairs.json', 'repairs', '{
  "schema_version": 1,
  "prepared_on": "2026-10-22",
  "academic_year": "AY2026/27",
  "scope": "Source-addressed repairs for the Toronto mapping rows detected by T010. Verified repairs recover metadata already implied by the source pairing; they do not create new exchange equivalences.",
  "notes": [
    "Before values are exact raw values at the recorded source pointer.",
    "The importer must refuse a repair whose before value does not match the raw source.",
    "Only status=verified entries may be applied. Unresolved rows remain quarantined.",
    "No original JSON source file is modified by this repair file."
  ],
  "source_file_sha256": {
    "data/mapping/canada/toronto.json": "ad1baec1ee241b7b2ba253a65874615f66471abb384bf93a3fb66fc1430ddef9"
  },
  "summary": {
    "verified_repairs": 5,
    "unresolved_repairs": 3,
    "affected_rows": 8,
    "verified_rows": [24, 50, 51, 52, 54],
    "unresolved_rows": [48, 49, 53]
  },
  "repairs": [
    {
      "repair_id": "toronto-024-csc311h1-units",
      "source_file": "data/mapping/canada/toronto.json",
      "mapping_index": 24,
      "source_sha256": "ad1baec1ee241b7b2ba253a65874615f66471abb384bf93a3fb66fc1430ddef9",
      "status": "verified",
      "issue_codes": ["partner_unit_conflict"],
      "unresolved_fields": [],
      "fields": {
        "partner_course.units": {
          "json_pointer": "/mappings/24/partner_course/units",
          "before": 3.0,
          "after": 0.5
        }
      },
      "evidence": [
        {
          "publisher": "University of Toronto, Faculty of Applied Science & Engineering",
          "url": "https://engineering.calendar.utoronto.ca/electrical-and-computer-engineering-aeescbaser",
          "page_title": "Electrical and Computer Engineering",
          "accessed_on": "2026-10-22",
          "academic_year": "2025-26",
          "quote": "CSC311H1 : Introduction to Machine Learning F/S 2 - 1 0.50",
          "supports": ["partner_course.code", "partner_course.title", "partner_course.units"]
        },
        {
          "publisher": "University of Toronto, Faculty of Arts & Science",
          "url": "https://artsci.calendar.utoronto.ca/course/csc311h1",
          "page_title": "CSC311H1 - Academic Calendar",
          "accessed_on": "2026-10-22",
          "academic_year": "2026-27",
          "quote": "CSC311H1: Introduction to Machine Learning ... Hours 24L/12T ... Previous Course Number CSC411H1",
          "supports": ["partner_course.code", "partner_course.title"]
        }
      ],
      "rationale": "The first CSC311H1 occurrence (row 11) records 0.5 units, and the University of Toronto Engineering calendar assigns CSC311H1 a fixed 0.50 credit value. Row 24''s 3.0 is therefore a data-entry error. The exchange pairing itself is unchanged."
    },
    {
      "repair_id": "toronto-048-software-engineering",
      "source_file": "data/mapping/canada/toronto.json",
      "mapping_index": 48,
      "source_sha256": "ad1baec1ee241b7b2ba253a65874615f66471abb384bf93a3fb66fc1430ddef9",
      "status": "unresolved",
      "issue_codes": ["invalid_nus_code", "missing_nus_title"],
      "unresolved_fields": ["nus_course.code", "nus_course.title"],
      "fields": {},
      "candidates": {
        "nus_course.code": ["CS2103", "CS2103T"],
        "nus_course.title": ["Software Engineering"]
      },
      "evidence": [
        {
          "publisher": "National University of Singapore, NUS Bulletin",
          "url": "https://www.nus.edu.sg/nusbulletin/ay202627/programmes/school-of-computing/undergraduate-education",
          "page_title": "Undergraduate Education - NUS Bulletin AY2026/27",
          "accessed_on": "2026-10-22",
          "academic_year": "AY2026/27",
          "quote": "CS2103T Software Engineering | 4",
          "supports": ["candidate:CS2103T"]
        },
        {
          "publisher": "National University of Singapore, School of Computing",
          "url": "https://www.comp.nus.edu.sg/programmes/ug/focus/software",
          "page_title": "Software Engineering - NUS Computing",
          "accessed_on": "2026-10-22",
          "academic_year": "current programme page",
          "quote": "CS2103 Software Engineering is the introductory course for this focus area (and a required course for all computer science students).",
          "supports": ["candidate:CS2103"]
        },
        {
          "publisher": "University of Toronto, Faculty of Arts & Science",
          "url": "https://artsci.calendar.utoronto.ca/course/csc207h1",
          "page_title": "CSC207H1 - Academic Calendar",
          "accessed_on": "2026-10-22",
          "academic_year": "2026-27",
          "quote": "CSC207H1: Software Design ... An introduction to software design and development concepts, methods, and tools using a statically-typed object-oriented programming language such as Java.",
          "supports": ["partner_course.code", "partner_course.title"]
        }
      ],
      "reason": "Both CS2103 and CS2103T are official NUS titles rendered as ''Software Engineering''. The source row records only the title, and the official pages disagree about which variant is the programme requirement, so neither code can be recovered without inference. The row stays quarantined."
    },
    {
      "repair_id": "toronto-049-discrete-structures",
      "source_file": "data/mapping/canada/toronto.json",
      "mapping_index": 49,
      "source_sha256": "ad1baec1ee241b7b2ba253a65874615f66471abb384bf93a3fb66fc1430ddef9",
      "status": "unresolved",
      "issue_codes": ["invalid_nus_code", "missing_nus_title"],
      "unresolved_fields": ["nus_course.code", "nus_course.title"],
      "fields": {},
      "candidates": {
        "nus_course.code": ["CS1231", "CS1231S"],
        "nus_course.title": ["Discrete Structures"]
      },
      "evidence": [
        {
          "publisher": "National University of Singapore, NUS Bulletin",
          "url": "https://www.nus.edu.sg/nusbulletin/ay202627/programmes/school-of-computing/undergraduate-education",
          "page_title": "Undergraduate Education - NUS Bulletin AY2026/27",
          "accessed_on": "2026-10-22",
          "academic_year": "AY2026/27",
          "quote": "CS1231S Discrete Structures | 4",
          "supports": ["candidate:CS1231S"]
        },
        {
          "publisher": "National University of Singapore, School of Computing",
          "url": "https://www.comp.nus.edu.sg/programmes/ug/minorc/minor-in-ai",
          "page_title": "Minor in Artificial Intelligence - NUS Computing",
          "accessed_on": "2026-10-22",
          "academic_year": "current programme page",
          "quote": "CS1231 Discrete Structures or MA1100/T Basic Discrete Mathematics",
          "supports": ["candidate:CS1231"]
        },
        {
          "publisher": "University of Toronto, Faculty of Arts & Science",
          "url": "https://artsci.calendar.utoronto.ca/course/csc165h1",
          "page_title": "CSC165H1 - Academic Calendar",
          "accessed_on": "2026-10-22",
          "academic_year": "2026-27",
          "quote": "CSC165H1: Mathematical Expression and Reasoning for Computer Science ... Introduction to abstraction and rigour.",
          "supports": ["partner_course.code", "partner_course.title"]
        }
      ],
      "reason": "Both CS1231 and CS1231S are official NUS titles rendered as ''Discrete Structures''. The source row does not identify the intended variant, and different official programme pages use different codes. The row stays quarantined."
    },
    {
      "repair_id": "toronto-050-cs3264",
      "source_file": "data/mapping/canada/toronto.json",
      "mapping_index": 50,
      "source_sha256": "ad1baec1ee241b7b2ba253a65874615f66471abb384bf93a3fb66fc1430ddef9",
      "status": "verified",
      "issue_codes": ["invalid_nus_code", "missing_nus_title"],
      "unresolved_fields": [],
      "fields": {
        "nus_course.code": {
          "json_pointer": "/mappings/50/nus_course/code",
          "before": "Foundations of Machine Le",
          "after": "CS3264"
        },
        "nus_course.title": {
          "json_pointer": "/mappings/50/nus_course/title",
          "before": null,
          "after": "Foundations of Machine Learning"
        }
      },
      "evidence": [
        {
          "publisher": "National University of Singapore, School of Computing",
          "url": "https://www.comp.nus.edu.sg/programmes/ug/ai/curr/",
          "page_title": "Curriculum (Prospective Students) - Artificial Intelligence",
          "accessed_on": "2026-10-22",
          "academic_year": "AY2026/27",
          "quote": "CS3264 Foundations of Machine Learning",
          "supports": ["nus_course.code", "nus_course.title"]
        },
        {
          "publisher": "National University of Singapore, School of Computing",
          "url": "https://www.comp.nus.edu.sg/programmes/ug/minorc/minor-in-ai",
          "page_title": "Minor in Artificial Intelligence - NUS Computing",
          "accessed_on": "2026-10-22",
          "academic_year": "current programme page",
          "quote": "CS3264 Foundations of Machine Learning",
          "supports": ["nus_course.code", "nus_course.title"]
        },
        {
          "publisher": "University of Toronto Scarborough, Academic Calendar",
          "url": "https://utsc.calendar.utoronto.ca/course/cscc11h3",
          "page_title": "CSCC11H3 - UTSC Academic Calendar",
          "accessed_on": "2026-10-22",
          "academic_year": "current calendar",
          "quote": "CSCC11H3: Introduction to Machine Learning and Data Mining",
          "supports": ["partner_course.code", "partner_course.title"]
        }
      ],
      "rationale": "The raw code field contains the truncated NUS title rather than a code. CS3264 is the unique official NUS course with the full title ''Foundations of Machine Learning'', and the source row already pairs CSCC11H3 with that course. Only the lost code and title are restored."
    },
    {
      "repair_id": "toronto-051-bt4240",
      "source_file": "data/mapping/canada/toronto.json",
      "mapping_index": 51,
      "source_sha256": "ad1baec1ee241b7b2ba253a65874615f66471abb384bf93a3fb66fc1430ddef9",
      "status": "verified",
      "issue_codes": ["invalid_nus_code", "missing_nus_title"],
      "unresolved_fields": [],
      "fields": {
        "nus_course.code": {
          "json_pointer": "/mappings/51/nus_course/code",
          "before": "Machine Learning for Pred",
          "after": "BT4240"
        },
        "nus_course.title": {
          "json_pointer": "/mappings/51/nus_course/title",
          "before": null,
          "after": "Machine Learning for Predictive Data Analytics"
        }
      },
      "evidence": [
        {
          "publisher": "National University of Singapore, School of Computing",
          "url": "https://www.comp.nus.edu.sg/programmes/ug/ba",
          "page_title": "Bachelor of Science in Business Analytics",
          "accessed_on": "2026-10-22",
          "academic_year": "AY2026/27",
          "quote": "BT4240 Machine Learning for Predictive Data Analytics",
          "supports": ["nus_course.code", "nus_course.title"]
        },
        {
          "publisher": "University of Toronto, Faculty of Applied Science & Engineering",
          "url": "https://engineering.calendar.utoronto.ca/course/mse403h1",
          "page_title": "MSE403H1 - Faculty of Applied Science and Engineering",
          "accessed_on": "2026-10-22",
          "academic_year": "2025-26",
          "quote": "MSE403H1: Advanced A.I. for Accelerated Materials Discovery",
          "supports": ["partner_course.code"]
        }
      ],
      "rationale": "The raw code field and existing rows 30, 31, and 40 show that ''Machine Learning for Pred'' is the truncated title for BT4240. The official NUS Business Analytics page gives the complete title. The partner course title in the source is older than the current U of T title; the exchange pairing is retained exactly as recorded.",
      "notes": [
        "The source partner title ''Data Sciences and Analytics for Materials Engineers'' differs from the current U of T title for MSE403H1. This repair does not change the partner side."
      ]
    },
    {
      "repair_id": "toronto-052-it2002",
      "source_file": "data/mapping/canada/toronto.json",
      "mapping_index": 52,
      "source_sha256": "ad1baec1ee241b7b2ba253a65874615f66471abb384bf93a3fb66fc1430ddef9",
      "status": "verified",
      "issue_codes": ["invalid_nus_code", "missing_nus_title"],
      "unresolved_fields": [],
      "fields": {
        "nus_course.code": {
          "json_pointer": "/mappings/52/nus_course/code",
          "before": "Database Technology and",
          "after": "IT2002"
        },
        "nus_course.title": {
          "json_pointer": "/mappings/52/nus_course/title",
          "before": null,
          "after": "Database Technology and Management"
        }
      },
      "evidence": [
        {
          "publisher": "National University of Singapore, College of Design and Engineering",
          "url": "https://cde.nus.edu.sg/ece/undergraduate/electrical-engineering/specialisations-and-minor/data-engineering",
          "page_title": "Minor in Data Engineering - Electrical and Computer Engineering",
          "accessed_on": "2026-10-22",
          "academic_year": "current programme page",
          "quote": "IT2002 Database Technology and Management or CS2102 Database Systems",
          "supports": ["nus_course.code", "nus_course.title"]
        },
        {
          "publisher": "National University of Singapore, Department of Industrial Systems Engineering and Management",
          "url": "https://cde.nus.edu.sg/isem/wp-content/uploads/sites/12/2026/06/Binder-BYOD1.pdf",
          "page_title": "Industrial and Systems Engineering specialisation requirements",
          "accessed_on": "2026-10-22",
          "academic_year": "AY2026/27",
          "quote": "IT2002 Database Technology and Management or CS2102 Database Systems 4",
          "supports": ["nus_course.code", "nus_course.title", "nus_course.units"]
        },
        {
          "publisher": "University of Toronto, Faculty of Arts & Science",
          "url": "https://artsci.calendar.utoronto.ca/course/csc343h1",
          "page_title": "CSC343H1 - Academic Calendar",
          "accessed_on": "2026-10-22",
          "academic_year": "2026-27",
          "quote": "CSC343H1: Introduction to Databases ... Introduction to database management systems. The relational data model.",
          "supports": ["partner_course.code", "partner_course.title"]
        }
      ],
      "rationale": "The raw code field contains the truncated NUS title. IT2002 is the unique official NUS course with the title ''Database Technology and Management''. Existing row 9 confirms the same title-to-code mapping. Only the lost code and title are restored."
    },
    {
      "repair_id": "toronto-053-programming-methodology",
      "source_file": "data/mapping/canada/toronto.json",
      "mapping_index": 53,
      "source_sha256": "ad1baec1ee241b7b2ba253a65874615f66471abb384bf93a3fb66fc1430ddef9",
      "status": "unresolved",
      "issue_codes": ["invalid_nus_code", "missing_nus_title"],
      "unresolved_fields": ["nus_course.code", "nus_course.title"],
      "fields": {},
      "candidates": {
        "nus_course.code": ["CS1010", "CS1010E", "CS1010S", "CS1101S"],
        "nus_course.title": ["Programming Methodology"],
        "partner_course.code": ["CSC108H1F"]
      },
      "evidence": [
        {
          "publisher": "National University of Singapore, School of Computing",
          "url": "https://www.comp.nus.edu.sg/programmes/ug/cs/curr/",
          "page_title": "Curriculum (Prospective Students) - Computer Science",
          "accessed_on": "2026-10-22",
          "academic_year": "AY2026/27",
          "quote": "CS1101S Programming Methodology",
          "supports": ["candidate:CS1101S"]
        },
        {
          "publisher": "National University of Singapore, School of Computing",
          "url": "https://www.comp.nus.edu.sg/programmes/ug/cs/curr/",
          "page_title": "Curriculum (Prospective Students) - Computer Science",
          "accessed_on": "2026-10-22",
          "academic_year": "AY2026/27",
          "quote": "CS1010 Programming Methodology",
          "supports": ["candidate:CS1010"]
        },
        {
          "publisher": "National University of Singapore, School of Computing",
          "url": "https://www.comp.nus.edu.sg/programmes/ug/minorc/ba-minor",
          "page_title": "Minor in Business Analytics - NUS Computing",
          "accessed_on": "2026-10-22",
          "academic_year": "current programme page",
          "quote": "CS1010S Programming Methodology",
          "supports": ["candidate:CS1010S"]
        },
        {
          "publisher": "National University of Singapore, College of Design and Engineering",
          "url": "https://cde.nus.edu.sg/me/wp-content/uploads/sites/11/2025/07/Sample-Schedule_RMI_AY2025-26-Onwards_20250624.pdf",
          "page_title": "Mechanical Engineering sample schedule",
          "accessed_on": "2026-10-22",
          "academic_year": "AY2025/26 onwards",
          "quote": "CS1010E Programming Methodology 4",
          "supports": ["candidate:CS1010E"]
        },
        {
          "publisher": "University of Toronto, Faculty of Arts & Science",
          "url": "https://artsci.calendar.utoronto.ca/course/csc108h1",
          "page_title": "CSC108H1 - Academic Calendar",
          "accessed_on": "2026-10-22",
          "academic_year": "2026-27",
          "quote": "CSC108H1: Introduction to Computer Programming ... Programming in a language such as Python.",
          "supports": ["partner_course.code", "partner_course.title"]
        }
      ],
      "reason": "Several official NUS courses share the title ''Programming Methodology'' and the source row does not identify which variant was intended. The partner code in the raw source is also truncated as ''108H1F'' instead of the official ''CSC108H1F''. The row stays quarantined and no partner-side correction is applied."
    },
    {
      "repair_id": "toronto-054-cs2100",
      "source_file": "data/mapping/canada/toronto.json",
      "mapping_index": 54,
      "source_sha256": "ad1baec1ee241b7b2ba253a65874615f66471abb384bf93a3fb66fc1430ddef9",
      "status": "verified",
      "issue_codes": ["invalid_nus_code", "missing_nus_title"],
      "unresolved_fields": [],
      "fields": {
        "nus_course.code": {
          "json_pointer": "/mappings/54/nus_course/code",
          "before": "Computer Organisation",
          "after": "CS2100"
        },
        "nus_course.title": {
          "json_pointer": "/mappings/54/nus_course/title",
          "before": null,
          "after": "Computer Organisation"
        }
      },
      "evidence": [
        {
          "publisher": "National University of Singapore, School of Computing",
          "url": "https://www.comp.nus.edu.sg/~cs2100/1_course_info/desc.html",
          "page_title": "CS2100 - Course Information - Description",
          "accessed_on": "2026-10-22",
          "academic_year": "AY2025/26 Semester 2",
          "quote": "CS2100 Computer Organisation ... Units: 4",
          "supports": ["nus_course.code", "nus_course.title", "nus_course.units"]
        },
        {
          "publisher": "National University of Singapore, NUS Bulletin",
          "url": "https://www.nus.edu.sg/nusbulletin/ay202627/programmes/school-of-computing/undergraduate-education",
          "page_title": "Undergraduate Education - NUS Bulletin AY2026/27",
          "accessed_on": "2026-10-22",
          "academic_year": "AY2026/27",
          "quote": "CS2100 Computer Organisation | 4",
          "supports": ["nus_course.code", "nus_course.title"]
        },
        {
          "publisher": "University of Toronto, Faculty of Applied Science & Engineering",
          "url": "https://engineering.calendar.utoronto.ca/course/ece243h1",
          "page_title": "ECE243H1 - Faculty of Applied Science and Engineering",
          "accessed_on": "2026-10-22",
          "academic_year": "2025-26",
          "quote": "ECE243H1: Computer Organization ... Basic computer structure. Design of central processing unit.",
          "supports": ["partner_course.code", "partner_course.title"]
        }
      ],
      "rationale": "The raw code field contains the NUS title. CS2100 is the official NUS course with the title ''Computer Organisation'', and existing row 19 confirms the same title-to-code mapping. Only the lost code and title are restored."
    }
  ]
}
', '{"notes": ["Before values are exact raw values at the recorded source pointer.", "The importer must refuse a repair whose before value does not match the raw source.", "Only status=verified entries may be applied. Unresolved rows remain quarantined.", "No original JSON source file is modified by this repair file."], "scope": "Source-addressed repairs for the Toronto mapping rows detected by T010. Verified repairs recover metadata already implied by the source pairing; they do not create new exchange equivalences.", "repairs": [{"fields": {"partner_course.units": {"after": 0.5, "before": 3.0, "json_pointer": "/mappings/24/partner_course/units"}}, "status": "verified", "evidence": [{"url": "https://engineering.calendar.utoronto.ca/electrical-and-computer-engineering-aeescbaser", "quote": "CSC311H1 : Introduction to Machine Learning F/S 2 - 1 0.50", "supports": ["partner_course.code", "partner_course.title", "partner_course.units"], "publisher": "University of Toronto, Faculty of Applied Science & Engineering", "page_title": "Electrical and Computer Engineering", "accessed_on": "2026-10-22", "academic_year": "2025-26"}, {"url": "https://artsci.calendar.utoronto.ca/course/csc311h1", "quote": "CSC311H1: Introduction to Machine Learning ... Hours 24L/12T ... Previous Course Number CSC411H1", "supports": ["partner_course.code", "partner_course.title"], "publisher": "University of Toronto, Faculty of Arts & Science", "page_title": "CSC311H1 - Academic Calendar", "accessed_on": "2026-10-22", "academic_year": "2026-27"}], "rationale": "The first CSC311H1 occurrence (row 11) records 0.5 units, and the University of Toronto Engineering calendar assigns CSC311H1 a fixed 0.50 credit value. Row 24''s 3.0 is therefore a data-entry error. The exchange pairing itself is unchanged.", "repair_id": "toronto-024-csc311h1-units", "issue_codes": ["partner_unit_conflict"], "source_file": "data/mapping/canada/toronto.json", "mapping_index": 24, "source_sha256": "ad1baec1ee241b7b2ba253a65874615f66471abb384bf93a3fb66fc1430ddef9", "unresolved_fields": []}, {"fields": {}, "reason": "Both CS2103 and CS2103T are official NUS titles rendered as ''Software Engineering''. The source row records only the title, and the official pages disagree about which variant is the programme requirement, so neither code can be recovered without inference. The row stays quarantined.", "status": "unresolved", "evidence": [{"url": "https://www.nus.edu.sg/nusbulletin/ay202627/programmes/school-of-computing/undergraduate-education", "quote": "CS2103T Software Engineering | 4", "supports": ["candidate:CS2103T"], "publisher": "National University of Singapore, NUS Bulletin", "page_title": "Undergraduate Education - NUS Bulletin AY2026/27", "accessed_on": "2026-10-22", "academic_year": "AY2026/27"}, {"url": "https://www.comp.nus.edu.sg/programmes/ug/focus/software", "quote": "CS2103 Software Engineering is the introductory course for this focus area (and a required course for all computer science students).", "supports": ["candidate:CS2103"], "publisher": "National University of Singapore, School of Computing", "page_title": "Software Engineering - NUS Computing", "accessed_on": "2026-10-22", "academic_year": "current programme page"}, {"url": "https://artsci.calendar.utoronto.ca/course/csc207h1", "quote": "CSC207H1: Software Design ... An introduction to software design and development concepts, methods, and tools using a statically-typed object-oriented programming language such as Java.", "supports": ["partner_course.code", "partner_course.title"], "publisher": "University of Toronto, Faculty of Arts & Science", "page_title": "CSC207H1 - Academic Calendar", "accessed_on": "2026-10-22", "academic_year": "2026-27"}], "repair_id": "toronto-048-software-engineering", "candidates": {"nus_course.code": ["CS2103", "CS2103T"], "nus_course.title": ["Software Engineering"]}, "issue_codes": ["invalid_nus_code", "missing_nus_title"], "source_file": "data/mapping/canada/toronto.json", "mapping_index": 48, "source_sha256": "ad1baec1ee241b7b2ba253a65874615f66471abb384bf93a3fb66fc1430ddef9", "unresolved_fields": ["nus_course.code", "nus_course.title"]}, {"fields": {}, "reason": "Both CS1231 and CS1231S are official NUS titles rendered as ''Discrete Structures''. The source row does not identify the intended variant, and different official programme pages use different codes. The row stays quarantined.", "status": "unresolved", "evidence": [{"url": "https://www.nus.edu.sg/nusbulletin/ay202627/programmes/school-of-computing/undergraduate-education", "quote": "CS1231S Discrete Structures | 4", "supports": ["candidate:CS1231S"], "publisher": "National University of Singapore, NUS Bulletin", "page_title": "Undergraduate Education - NUS Bulletin AY2026/27", "accessed_on": "2026-10-22", "academic_year": "AY2026/27"}, {"url": "https://www.comp.nus.edu.sg/programmes/ug/minorc/minor-in-ai", "quote": "CS1231 Discrete Structures or MA1100/T Basic Discrete Mathematics", "supports": ["candidate:CS1231"], "publisher": "National University of Singapore, School of Computing", "page_title": "Minor in Artificial Intelligence - NUS Computing", "accessed_on": "2026-10-22", "academic_year": "current programme page"}, {"url": "https://artsci.calendar.utoronto.ca/course/csc165h1", "quote": "CSC165H1: Mathematical Expression and Reasoning for Computer Science ... Introduction to abstraction and rigour.", "supports": ["partner_course.code", "partner_course.title"], "publisher": "University of Toronto, Faculty of Arts & Science", "page_title": "CSC165H1 - Academic Calendar", "accessed_on": "2026-10-22", "academic_year": "2026-27"}], "repair_id": "toronto-049-discrete-structures", "candidates": {"nus_course.code": ["CS1231", "CS1231S"], "nus_course.title": ["Discrete Structures"]}, "issue_codes": ["invalid_nus_code", "missing_nus_title"], "source_file": "data/mapping/canada/toronto.json", "mapping_index": 49, "source_sha256": "ad1baec1ee241b7b2ba253a65874615f66471abb384bf93a3fb66fc1430ddef9", "unresolved_fields": ["nus_course.code", "nus_course.title"]}, {"fields": {"nus_course.code": {"after": "CS3264", "before": "Foundations of Machine Le", "json_pointer": "/mappings/50/nus_course/code"}, "nus_course.title": {"after": "Foundations of Machine Learning", "before": null, "json_pointer": "/mappings/50/nus_course/title"}}, "status": "verified", "evidence": [{"url": "https://www.comp.nus.edu.sg/programmes/ug/ai/curr/", "quote": "CS3264 Foundations of Machine Learning", "supports": ["nus_course.code", "nus_course.title"], "publisher": "National University of Singapore, School of Computing", "page_title": "Curriculum (Prospective Students) - Artificial Intelligence", "accessed_on": "2026-10-22", "academic_year": "AY2026/27"}, {"url": "https://www.comp.nus.edu.sg/programmes/ug/minorc/minor-in-ai", "quote": "CS3264 Foundations of Machine Learning", "supports": ["nus_course.code", "nus_course.title"], "publisher": "National University of Singapore, School of Computing", "page_title": "Minor in Artificial Intelligence - NUS Computing", "accessed_on": "2026-10-22", "academic_year": "current programme page"}, {"url": "https://utsc.calendar.utoronto.ca/course/cscc11h3", "quote": "CSCC11H3: Introduction to Machine Learning and Data Mining", "supports": ["partner_course.code", "partner_course.title"], "publisher": "University of Toronto Scarborough, Academic Calendar", "page_title": "CSCC11H3 - UTSC Academic Calendar", "accessed_on": "2026-10-22", "academic_year": "current calendar"}], "rationale": "The raw code field contains the truncated NUS title rather than a code. CS3264 is the unique official NUS course with the full title ''Foundations of Machine Learning'', and the source row already pairs CSCC11H3 with that course. Only the lost code and title are restored.", "repair_id": "toronto-050-cs3264", "issue_codes": ["invalid_nus_code", "missing_nus_title"], "source_file": "data/mapping/canada/toronto.json", "mapping_index": 50, "source_sha256": "ad1baec1ee241b7b2ba253a65874615f66471abb384bf93a3fb66fc1430ddef9", "unresolved_fields": []}, {"notes": ["The source partner title ''Data Sciences and Analytics for Materials Engineers'' differs from the current U of T title for MSE403H1. This repair does not change the partner side."], "fields": {"nus_course.code": {"after": "BT4240", "before": "Machine Learning for Pred", "json_pointer": "/mappings/51/nus_course/code"}, "nus_course.title": {"after": "Machine Learning for Predictive Data Analytics", "before": null, "json_pointer": "/mappings/51/nus_course/title"}}, "status": "verified", "evidence": [{"url": "https://www.comp.nus.edu.sg/programmes/ug/ba", "quote": "BT4240 Machine Learning for Predictive Data Analytics", "supports": ["nus_course.code", "nus_course.title"], "publisher": "National University of Singapore, School of Computing", "page_title": "Bachelor of Science in Business Analytics", "accessed_on": "2026-10-22", "academic_year": "AY2026/27"}, {"url": "https://engineering.calendar.utoronto.ca/course/mse403h1", "quote": "MSE403H1: Advanced A.I. for Accelerated Materials Discovery", "supports": ["partner_course.code"], "publisher": "University of Toronto, Faculty of Applied Science & Engineering", "page_title": "MSE403H1 - Faculty of Applied Science and Engineering", "accessed_on": "2026-10-22", "academic_year": "2025-26"}], "rationale": "The raw code field and existing rows 30, 31, and 40 show that ''Machine Learning for Pred'' is the truncated title for BT4240. The official NUS Business Analytics page gives the complete title. The partner course title in the source is older than the current U of T title; the exchange pairing is retained exactly as recorded.", "repair_id": "toronto-051-bt4240", "issue_codes": ["invalid_nus_code", "missing_nus_title"], "source_file": "data/mapping/canada/toronto.json", "mapping_index": 51, "source_sha256": "ad1baec1ee241b7b2ba253a65874615f66471abb384bf93a3fb66fc1430ddef9", "unresolved_fields": []}, {"fields": {"nus_course.code": {"after": "IT2002", "before": "Database Technology and", "json_pointer": "/mappings/52/nus_course/code"}, "nus_course.title": {"after": "Database Technology and Management", "before": null, "json_pointer": "/mappings/52/nus_course/title"}}, "status": "verified", "evidence": [{"url": "https://cde.nus.edu.sg/ece/undergraduate/electrical-engineering/specialisations-and-minor/data-engineering", "quote": "IT2002 Database Technology and Management or CS2102 Database Systems", "supports": ["nus_course.code", "nus_course.title"], "publisher": "National University of Singapore, College of Design and Engineering", "page_title": "Minor in Data Engineering - Electrical and Computer Engineering", "accessed_on": "2026-10-22", "academic_year": "current programme page"}, {"url": "https://cde.nus.edu.sg/isem/wp-content/uploads/sites/12/2026/06/Binder-BYOD1.pdf", "quote": "IT2002 Database Technology and Management or CS2102 Database Systems 4", "supports": ["nus_course.code", "nus_course.title", "nus_course.units"], "publisher": "National University of Singapore, Department of Industrial Systems Engineering and Management", "page_title": "Industrial and Systems Engineering specialisation requirements", "accessed_on": "2026-10-22", "academic_year": "AY2026/27"}, {"url": "https://artsci.calendar.utoronto.ca/course/csc343h1", "quote": "CSC343H1: Introduction to Databases ... Introduction to database management systems. The relational data model.", "supports": ["partner_course.code", "partner_course.title"], "publisher": "University of Toronto, Faculty of Arts & Science", "page_title": "CSC343H1 - Academic Calendar", "accessed_on": "2026-10-22", "academic_year": "2026-27"}], "rationale": "The raw code field contains the truncated NUS title. IT2002 is the unique official NUS course with the title ''Database Technology and Management''. Existing row 9 confirms the same title-to-code mapping. Only the lost code and title are restored.", "repair_id": "toronto-052-it2002", "issue_codes": ["invalid_nus_code", "missing_nus_title"], "source_file": "data/mapping/canada/toronto.json", "mapping_index": 52, "source_sha256": "ad1baec1ee241b7b2ba253a65874615f66471abb384bf93a3fb66fc1430ddef9", "unresolved_fields": []}, {"fields": {}, "reason": "Several official NUS courses share the title ''Programming Methodology'' and the source row does not identify which variant was intended. The partner code in the raw source is also truncated as ''108H1F'' instead of the official ''CSC108H1F''. The row stays quarantined and no partner-side correction is applied.", "status": "unresolved", "evidence": [{"url": "https://www.comp.nus.edu.sg/programmes/ug/cs/curr/", "quote": "CS1101S Programming Methodology", "supports": ["candidate:CS1101S"], "publisher": "National University of Singapore, School of Computing", "page_title": "Curriculum (Prospective Students) - Computer Science", "accessed_on": "2026-10-22", "academic_year": "AY2026/27"}, {"url": "https://www.comp.nus.edu.sg/programmes/ug/cs/curr/", "quote": "CS1010 Programming Methodology", "supports": ["candidate:CS1010"], "publisher": "National University of Singapore, School of Computing", "page_title": "Curriculum (Prospective Students) - Computer Science", "accessed_on": "2026-10-22", "academic_year": "AY2026/27"}, {"url": "https://www.comp.nus.edu.sg/programmes/ug/minorc/ba-minor", "quote": "CS1010S Programming Methodology", "supports": ["candidate:CS1010S"], "publisher": "National University of Singapore, School of Computing", "page_title": "Minor in Business Analytics - NUS Computing", "accessed_on": "2026-10-22", "academic_year": "current programme page"}, {"url": "https://cde.nus.edu.sg/me/wp-content/uploads/sites/11/2025/07/Sample-Schedule_RMI_AY2025-26-Onwards_20250624.pdf", "quote": "CS1010E Programming Methodology 4", "supports": ["candidate:CS1010E"], "publisher": "National University of Singapore, College of Design and Engineering", "page_title": "Mechanical Engineering sample schedule", "accessed_on": "2026-10-22", "academic_year": "AY2025/26 onwards"}, {"url": "https://artsci.calendar.utoronto.ca/course/csc108h1", "quote": "CSC108H1: Introduction to Computer Programming ... Programming in a language such as Python.", "supports": ["partner_course.code", "partner_course.title"], "publisher": "University of Toronto, Faculty of Arts & Science", "page_title": "CSC108H1 - Academic Calendar", "accessed_on": "2026-10-22", "academic_year": "2026-27"}], "repair_id": "toronto-053-programming-methodology", "candidates": {"nus_course.code": ["CS1010", "CS1010E", "CS1010S", "CS1101S"], "nus_course.title": ["Programming Methodology"], "partner_course.code": ["CSC108H1F"]}, "issue_codes": ["invalid_nus_code", "missing_nus_title"], "source_file": "data/mapping/canada/toronto.json", "mapping_index": 53, "source_sha256": "ad1baec1ee241b7b2ba253a65874615f66471abb384bf93a3fb66fc1430ddef9", "unresolved_fields": ["nus_course.code", "nus_course.title"]}, {"fields": {"nus_course.code": {"after": "CS2100", "before": "Computer Organisation", "json_pointer": "/mappings/54/nus_course/code"}, "nus_course.title": {"after": "Computer Organisation", "before": null, "json_pointer": "/mappings/54/nus_course/title"}}, "status": "verified", "evidence": [{"url": "https://www.comp.nus.edu.sg/~cs2100/1_course_info/desc.html", "quote": "CS2100 Computer Organisation ... Units: 4", "supports": ["nus_course.code", "nus_course.title", "nus_course.units"], "publisher": "National University of Singapore, School of Computing", "page_title": "CS2100 - Course Information - Description", "accessed_on": "2026-10-22", "academic_year": "AY2025/26 Semester 2"}, {"url": "https://www.nus.edu.sg/nusbulletin/ay202627/programmes/school-of-computing/undergraduate-education", "quote": "CS2100 Computer Organisation | 4", "supports": ["nus_course.code", "nus_course.title"], "publisher": "National University of Singapore, NUS Bulletin", "page_title": "Undergraduate Education - NUS Bulletin AY2026/27", "accessed_on": "2026-10-22", "academic_year": "AY2026/27"}, {"url": "https://engineering.calendar.utoronto.ca/course/ece243h1", "quote": "ECE243H1: Computer Organization ... Basic computer structure. Design of central processing unit.", "supports": ["partner_course.code", "partner_course.title"], "publisher": "University of Toronto, Faculty of Applied Science & Engineering", "page_title": "ECE243H1 - Faculty of Applied Science and Engineering", "accessed_on": "2026-10-22", "academic_year": "2025-26"}], "rationale": "The raw code field contains the NUS title. CS2100 is the official NUS course with the title ''Computer Organisation'', and existing row 19 confirms the same title-to-code mapping. Only the lost code and title are restored.", "repair_id": "toronto-054-cs2100", "issue_codes": ["invalid_nus_code", "missing_nus_title"], "source_file": "data/mapping/canada/toronto.json", "mapping_index": 54, "source_sha256": "ad1baec1ee241b7b2ba253a65874615f66471abb384bf93a3fb66fc1430ddef9", "unresolved_fields": []}], "summary": {"affected_rows": 8, "verified_rows": [24, 50, 51, 52, 54], "unresolved_rows": [48, 49, 53], "verified_repairs": 5, "unresolved_repairs": 3}, "prepared_on": "2026-10-22", "academic_year": "AY2026/27", "schema_version": 1, "source_file_sha256": {"data/mapping/canada/toronto.json": "ad1baec1ee241b7b2ba253a65874615f66471abb384bf93a3fb66fc1430ddef9"}}', '61268be6b39c1effc644d72c8cc4787287cdbcafc86d32fb3c48814d48064a3e', 20732, '2026-10-23 23:01:40.872227+08');


--
-- Data for Name: catalog_source_rows; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (1, 3, 0, '{"faculty": "School of Computing", "nus_course": {"code": "IS4302", "title": "Blockchain and Distributed"}, "source_page": 1, "partner_course": {"code": "BUSN5001", "title": "Blockchain and Distributed Ledger Technologies in Business", "units": 6.0}}', 'IS4302', 'BUSN5001', 'Blockchain and Distributed', 'Blockchain and Distributed Ledger Technologies in Business', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (2, 3, 1, '{"faculty": "School of Computing", "nus_course": {"code": "CS2102", "title": "Database Systems"}, "source_page": 1, "partner_course": {"code": "CITS1402", "title": "Relational Database Management Systems", "units": 6.0}}', 'CS2102', 'CITS1402', 'Database Systems', 'Relational Database Management Systems', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (3, 3, 2, '{"faculty": "School of Computing", "nus_course": {"code": "CS2040", "title": "Data Structures and Algor"}, "source_page": 1, "partner_course": {"code": "CITS2200", "title": "Data Structures and Algorithms", "units": 6.0}}', 'CS2040', 'CITS2200', 'Data Structures and Algor', 'Data Structures and Algorithms', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (4, 3, 3, '{"faculty": "School of Computing", "nus_course": {"code": "BT4014", "title": "Analytics Driven Design of"}, "source_page": 1, "partner_course": {"code": "CITS3001", "title": "Algorithms, Agents and Artificial Intelligence", "units": 6.0}}', 'BT4014', 'CITS3001', 'Analytics Driven Design of', 'Algorithms, Agents and Artificial Intelligence', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (5, 3, 4, '{"faculty": "School of Computing", "nus_course": {"code": "CS3243", "title": "Introduction to Artificial In"}, "source_page": 1, "partner_course": {"code": "CITS3001", "title": "Algorithms, Agents and Artificial Intelligence", "units": 6.0}}', 'CS3243', 'CITS3001', 'Introduction to Artificial In', 'Algorithms, Agents and Artificial Intelligence', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (6, 3, 5, '{"faculty": "School of Computing", "nus_course": {"code": "CS2105", "title": "Introduction to Computer"}, "source_page": 1, "partner_course": {"code": "CITS3002", "title": "Computer Networks", "units": 6.0}}', 'CS2105', 'CITS3002', 'Introduction to Computer', 'Computer Networks', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (7, 3, 6, '{"faculty": "School of Computing", "nus_course": {"code": "CS3235", "title": "Computer Security"}, "source_page": 1, "partner_course": {"code": "CITS3004", "title": "Cybersecurity", "units": 6.0}}', 'CS3235', 'CITS3004', 'Computer Security', 'Cybersecurity', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (8, 3, 7, '{"faculty": "School of Computing", "nus_course": {"code": "IFS4103", "title": "Penetration Testing Practic"}, "source_page": 1, "partner_course": {"code": "CITS3006", "title": "Penetration Testing", "units": 6.0}}', 'IFS4103', 'CITS3006', 'Penetration Testing Practic', 'Penetration Testing', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (9, 3, 8, '{"faculty": "School of Computing", "nus_course": {"code": "CS4239", "title": "Software Security"}, "source_page": 1, "partner_course": {"code": "CITS3007", "title": "Secure Coding", "units": 6.0}}', 'CS4239', 'CITS3007', 'Software Security', 'Secure Coding', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (10, 3, 9, '{"faculty": "School of Computing", "nus_course": {"code": "CS3213", "title": "Software Requirements Sp"}, "source_page": 1, "partner_course": {"code": "CITS3301", "title": "Software Requirements and Design", "units": 6.0}}', 'CS3213', 'CITS3301', 'Software Requirements Sp', 'Software Requirements and Design', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (11, 3, 10, '{"faculty": "School of Computing", "nus_course": {"code": "BT4014", "title": "Analytics Driven Design of"}, "source_page": 1, "partner_course": {"code": "CITS4009", "title": "Computational Data Analysis", "units": 6.0}}', 'BT4014', 'CITS4009', 'Analytics Driven Design of', 'Computational Data Analysis', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (12, 3, 11, '{"faculty": "School of Computing", "nus_course": {"code": "BT4014", "title": "Analytics Driven Design of"}, "source_page": 1, "partner_course": {"code": "CITS4404", "title": "Artificial Intelligence and Adaptive Systems", "units": 6.0}}', 'BT4014', 'CITS4404', 'Analytics Driven Design of', 'Artificial Intelligence and Adaptive Systems', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (13, 3, 12, '{"faculty": "School of Computing", "nus_course": {"code": "CS3243", "title": "Introduction to Artificial In"}, "source_page": 1, "partner_course": {"code": "CITS4404", "title": "Artificial Intelligence and Adaptive Systems", "units": 6.0}}', 'CS3243', 'CITS4404', 'Introduction to Artificial In', 'Artificial Intelligence and Adaptive Systems', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (14, 3, 13, '{"faculty": "School of Computing", "nus_course": {"code": "IS4242", "title": "Intelligent Systems and Te"}, "source_page": 1, "partner_course": {"code": "CITS4404", "title": "Artificial Intelligence and Adaptive Systems", "units": 6.0}}', 'IS4242', 'CITS4404', 'Intelligent Systems and Te', 'Artificial Intelligence and Adaptive Systems', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (15, 3, 14, '{"faculty": "School of Computing", "nus_course": {"code": "CS4222", "title": "Wireless Networking"}, "source_page": 1, "partner_course": {"code": "CITS4419", "title": "Mobile and Wireless Computing", "units": 6.0}}', 'CS4222', 'CITS4419', 'Wireless Networking', 'Mobile and Wireless Computing', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (16, 3, 15, '{"faculty": "School of Computing", "nus_course": {"code": "CS5224", "title": "Cloud Computing"}, "source_page": 1, "partner_course": {"code": "CITS5503", "title": "Cloud Computing", "units": 6.0}}', 'CS5224', 'CITS5503', 'Cloud Computing', 'Cloud Computing', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (17, 3, 16, '{"faculty": "School of Computing", "nus_course": {"code": "CS3237", "title": "Introduction to Internet of"}, "source_page": 1, "partner_course": {"code": "CITS5506", "title": "The Internet of Things", "units": 6.0}}', 'CS3237', 'CITS5506', 'Introduction to Internet of', 'The Internet of Things', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (18, 3, 17, '{"faculty": "School of Computing", "nus_course": {"code": "CS3210", "title": "Parallel Computing"}, "source_page": 1, "partner_course": {"code": "CITS5507", "title": "High Performance Computing", "units": 6.0}}', 'CS3210', 'CITS5507', 'Parallel Computing', 'High Performance Computing', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (19, 3, 18, '{"faculty": "School of Computing", "nus_course": {"code": "CS2030", "title": "Programming Methodology"}, "source_page": 1, "partner_course": {"code": "CTIS2005", "title": "Object Oriented Programming", "units": 6.0}}', 'CS2030', 'CTIS2005', 'Programming Methodology', 'Object Oriented Programming', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (20, 3, 19, '{"faculty": "School of Computing", "nus_course": {"code": "BT4015", "title": "Geospatial Analytics"}, "source_page": 1, "partner_course": {"code": "ENVT4411", "title": "Geographic Information Systems Applications", "units": 6.0}}', 'BT4015', 'ENVT4411', 'Geospatial Analytics', 'Geographic Information Systems Applications', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (21, 3, 20, '{"faculty": "School of Computing", "nus_course": {"code": "BT4015", "title": "Geospatial Analytics"}, "source_page": 1, "partner_course": {"code": "ENVT5566", "title": "Advanced Spatial and Environmental Modelling", "units": 6.0}}', 'BT4015', 'ENVT5566', 'Geospatial Analytics', 'Advanced Spatial and Environmental Modelling', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (22, 3, 21, '{"faculty": "School of Computing", "nus_course": {"code": "BT4013", "title": "Analytics for Capital Marke"}, "source_page": 1, "partner_course": {"code": "FINA4491", "title": "Capital Markets Research", "units": 6.0}}', 'BT4013', 'FINA4491', 'Analytics for Capital Marke', 'Capital Markets Research', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (23, 3, 22, '{"faculty": "School of Computing", "nus_course": {"code": "BT4015", "title": "Geospatial Analytics"}, "source_page": 1, "partner_course": {"code": "GEOG2201", "title": "Geographic Information Systems", "units": 6.0}}', 'BT4015', 'GEOG2201', 'Geospatial Analytics', 'Geographic Information Systems', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (24, 3, 23, '{"faculty": "School of Computing", "nus_course": {"code": "BT4015", "title": "Geospatial Analytics"}, "source_page": 1, "partner_course": {"code": "GEOG3300", "title": "Advanced Spatial Analysis", "units": 6.0}}', 'BT4015', 'GEOG3300', 'Geospatial Analytics', 'Advanced Spatial Analysis', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (25, 3, 24, '{"faculty": "School of Computing", "nus_course": {"code": "IS4241", "title": "Social Media Network Ana"}, "source_page": 1, "partner_course": {"code": "MATH3002", "title": "Network Science", "units": 6.0}}', 'IS4241', 'MATH3002', 'Social Media Network Ana', 'Network Science', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (26, 3, 25, '{"faculty": "School of Computing", "nus_course": {"code": "BT4211", "title": "Data-Driven Marketing"}, "source_page": 1, "partner_course": {"code": "MKTG2305", "title": "Marketing Research", "units": 6.0}}', 'BT4211', 'MKTG2305', 'Data-Driven Marketing', 'Marketing Research', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (27, 3, 26, '{"faculty": "School of Computing", "nus_course": {"code": "BT4211", "title": "Data-Driven Marketing"}, "source_page": 1, "partner_course": {"code": "MKTG3307", "title": "Digital Marketing", "units": 6.0}}', 'BT4211', 'MKTG3307', 'Data-Driven Marketing', 'Digital Marketing', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (28, 3, 27, '{"faculty": "School of Computing", "nus_course": {"code": "BT4211", "title": "Data-Driven Marketing"}, "source_page": 1, "partner_course": {"code": "MKTG3308", "title": "Marketing Analytics", "units": 6.0}}', 'BT4211', 'MKTG3308', 'Data-Driven Marketing', 'Marketing Analytics', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (29, 3, 28, '{"faculty": "School of Computing", "nus_course": {"code": "BT4211", "title": "Data-Driven Marketing"}, "source_page": 1, "partner_course": {"code": "MKTG5504", "title": "Big Data in Marketing", "units": 6.0}}', 'BT4211', 'MKTG5504', 'Data-Driven Marketing', 'Big Data in Marketing', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (30, 3, 29, '{"faculty": "School of Computing", "nus_course": {"code": "BT4015", "title": "Geospatial Analytics"}, "source_page": 1, "partner_course": {"code": "STAT3063", "title": "Spatial Statistics and Modeling", "units": 6.0}}', 'BT4015', 'STAT3063', 'Geospatial Analytics', 'Spatial Statistics and Modeling', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (31, 3, 30, '{"faculty": "School of Computing", "nus_course": {"code": "BT4240", "title": "Machine Learning for Pred"}, "source_page": 1, "partner_course": {"code": "STAT3406", "title": "Applied Statistics and Data Visualisation", "units": 6.0}}', 'BT4240', 'STAT3406', 'Machine Learning for Pred', 'Applied Statistics and Data Visualisation', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (32, 3, 31, '{"faculty": "School of Computing", "nus_course": {"code": "BT4240", "title": "Machine Learning for Pred"}, "source_page": 1, "partner_course": {"code": "STAT4064", "title": "Applied Predictive Modeling", "units": 6.0}}', 'BT4240', 'STAT4064', 'Machine Learning for Pred', 'Applied Predictive Modeling', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (33, 4, 0, '{"faculty": "School of Computing", "nus_course": {"code": "CS2106", "title": "Introduction to Operating"}, "source_page": 1, "partner_course": {"code": "ECE344H1", "title": "Operating Systems", "units": 0.5}}', 'CS2106', 'ECE344H1', 'Introduction to Operating', 'Operating Systems', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (34, 4, 1, '{"faculty": "School of Computing", "nus_course": {"code": "CS2103", "title": "Software Engineering"}, "source_page": 1, "partner_course": {"code": "CSC444H1", "title": "Software Engineering", "units": 0.5}}', 'CS2103', 'CSC444H1', 'Software Engineering', 'Software Engineering', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (35, 4, 2, '{"faculty": "School of Computing", "nus_course": {"code": "CS2104", "title": "Programming Language C"}, "source_page": 1, "partner_course": {"code": "CSC326H1", "title": "Programming Languages", "units": 0.5}}', 'CS2104', 'CSC326H1', 'Programming Language C', 'Programming Languages', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (36, 4, 3, '{"faculty": "School of Computing", "nus_course": {"code": "CS3247", "title": "Game Development"}, "source_page": 1, "partner_course": {"code": "CSC404H1", "title": "Introduction to Video Game Design", "units": 0.5}}', 'CS3247', 'CSC404H1', 'Game Development', 'Introduction to Video Game Design', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (91, 5, 3, '{"faculty": "School of Computing", "nus_course": {"code": "CS2105", "title": "Introduction to Computer"}, "source_page": 1, "partner_course": {"code": "T019001", "title": "Information Network-E2", "units": 2.0}}', 'CS2105', 'T019001', 'Introduction to Computer', 'Information Network-E2', NULL, 2.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (37, 4, 4, '{"faculty": "School of Computing", "nus_course": {"code": "CS3244", "title": "Machine Learning"}, "source_page": 1, "partner_course": {"code": "ROB313H1", "title": "Introduction to Learning from Data", "units": 0.5}}', 'CS3244', 'ROB313H1', 'Machine Learning', 'Introduction to Learning from Data', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (38, 4, 5, '{"faculty": "School of Computing", "nus_course": {"code": "CS4249", "title": "Quantitative Methods of H"}, "source_page": 1, "partner_course": {"code": "CSC428H1-S", "title": "Human-Computer Interaction", "units": 0.5}}', 'CS4249', 'CSC428H1-S', 'Quantitative Methods of H', 'Human-Computer Interaction', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (39, 4, 6, '{"faculty": "School of Computing", "nus_course": {"code": "CS4243", "title": "Computer Vision and Patte"}, "source_page": 1, "partner_course": {"code": "CSC420H1", "title": "Introduction to Image Understanding", "units": 0.5}}', 'CS4243', 'CSC420H1', 'Computer Vision and Patte', 'Introduction to Image Understanding', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (40, 4, 7, '{"faculty": "School of Computing", "nus_course": {"code": "CS5242", "title": "Neural Networks and Deep"}, "source_page": 1, "partner_course": {"code": "CSC413H1", "title": "\" Neural Networks and Deep Learning\"", "units": 0.5}}', 'CS5242', 'CSC413H1', 'Neural Networks and Deep', '" Neural Networks and Deep Learning"', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (41, 4, 8, '{"faculty": "School of Computing", "nus_course": {"code": "BT3103", "title": "Application Systems Deve"}, "source_page": 1, "partner_course": {"code": "CSC309H1", "title": "Programming on the Web", "units": 0.5}}', 'BT3103', 'CSC309H1', 'Application Systems Deve', 'Programming on the Web', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (42, 4, 9, '{"faculty": "School of Computing", "nus_course": {"code": "BT3102", "title": "Computational Methods fo"}, "source_page": 1, "partner_course": {"code": "CSC412", "title": "Probabilistic Learning and Reasoning", "units": 0.5}}', 'BT3102', 'CSC412', 'Computational Methods fo', 'Probabilistic Learning and Reasoning', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (43, 4, 10, '{"faculty": "School of Computing", "nus_course": {"code": "IS3107", "title": "Data Engineering"}, "source_page": 1, "partner_course": {"code": "CSC443H1", "title": "Database System Technology", "units": 0.5}}', 'IS3107', 'CSC443H1', 'Data Engineering', 'Database System Technology', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (44, 4, 11, '{"faculty": "School of Computing", "nus_course": {"code": "CS3264", "title": "Foundations of Machine Le"}, "source_page": 1, "partner_course": {"code": "CSC311H1", "title": "Introduction to Machine Learning", "units": 0.5}}', 'CS3264', 'CSC311H1', 'Foundations of Machine Le', 'Introduction to Machine Learning', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (45, 4, 12, '{"faculty": "School of Computing", "nus_course": {"code": "CS4248", "title": "Introduction to Large Lang"}, "source_page": 1, "partner_course": {"code": "CSC401H1", "title": "Natural Language Computing", "units": 0.5}}', 'CS4248', 'CSC401H1', 'Introduction to Large Lang', 'Natural Language Computing', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (46, 4, 13, '{"faculty": "School of Computing", "nus_course": {"code": "CS3213", "title": "Software Requirements Sp"}, "source_page": 1, "partner_course": {"code": "CSC302H1", "title": "Engineering Large Software Systems", "units": 0.5}}', 'CS3213', 'CSC302H1', 'Software Requirements Sp', 'Engineering Large Software Systems', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (47, 4, 14, '{"faculty": "School of Computing", "nus_course": {"code": "CS3263", "title": "Foundations of Artificial In"}, "source_page": 1, "partner_course": {"code": "CSC384H1", "title": "Introduction to Artificial Intelligence", "units": 0.5}}', 'CS3263', 'CSC384H1', 'Foundations of Artificial In', 'Introduction to Artificial Intelligence', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (48, 4, 15, '{"faculty": "School of Computing", "nus_course": {"code": "CS4211", "title": "Formal Methods for Softwa"}, "source_page": 1, "partner_course": {"code": "CSC3465H1", "title": "Formal Methods in Software Design", "units": 0.5}}', 'CS4211', 'CSC3465H1', 'Formal Methods for Softwa', 'Formal Methods in Software Design', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (49, 4, 16, '{"faculty": "School of Computing", "nus_course": {"code": "CS2106", "title": "Introduction to Operating"}, "source_page": 1, "partner_course": {"code": "CSC369H1", "title": "Operating Systems", "units": 0.5}}', 'CS2106', 'CSC369H1', 'Introduction to Operating', 'Operating Systems', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (50, 4, 17, '{"faculty": "School of Computing", "nus_course": {"code": "BT2101", "title": "Econometrics Modeling for"}, "source_page": 1, "partner_course": {"code": "ECO375H1", "title": "Foundations of Econometrics", "units": 0.5}}', 'BT2101', 'ECO375H1', 'Econometrics Modeling for', 'Foundations of Econometrics', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (51, 4, 18, '{"faculty": "School of Computing", "nus_course": {"code": "CS4220", "title": "Knowledge Discovery Meth"}, "source_page": 1, "partner_course": {"code": "BCB420H1", "title": "Computational Systems Biology", "units": 0.5}}', 'CS4220', 'BCB420H1', 'Knowledge Discovery Meth', 'Computational Systems Biology', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (52, 4, 19, '{"faculty": "School of Computing", "nus_course": {"code": "CS2100", "title": "Computer Organisation"}, "source_page": 1, "partner_course": {"code": "ECE352", "title": "Computer Organization", "units": 3.0}}', 'CS2100', 'ECE352', 'Computer Organisation', 'Computer Organization', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (53, 4, 20, '{"faculty": "School of Computing", "nus_course": {"code": "CS3230", "title": "Design and Analysis of Alg"}, "source_page": 1, "partner_course": {"code": "ECE358", "title": "Foundations of Computing", "units": 3.0}}', 'CS3230', 'ECE358', 'Design and Analysis of Alg', 'Foundations of Computing', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (54, 4, 21, '{"faculty": "School of Computing", "nus_course": {"code": "CS4236", "title": "Cryptography in Practice:"}, "source_page": 1, "partner_course": {"code": "CSC322H5", "title": "Introduction to Algebraic Cryptography", "units": 3.0}}', 'CS4236', 'CSC322H5', 'Cryptography in Practice:', 'Introduction to Algebraic Cryptography', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (55, 4, 22, '{"faculty": "School of Computing", "nus_course": {"code": "CS2105", "title": "Introduction to Computer"}, "source_page": 1, "partner_course": {"code": "CSC358H1", "title": "Principles of Computer Networks", "units": 3.0}}', 'CS2105', 'CSC358H1', 'Introduction to Computer', 'Principles of Computer Networks', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (56, 4, 23, '{"faculty": "School of Computing", "nus_course": {"code": "CS3235", "title": "Computer Security"}, "source_page": 1, "partner_course": {"code": "ECE568H1", "title": "Computer Security", "units": 3.0}}', 'CS3235', 'ECE568H1', 'Computer Security', 'Computer Security', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (57, 4, 24, '{"faculty": "School of Computing", "nus_course": {"code": "CS3244", "title": "Machine Learning"}, "source_page": 1, "partner_course": {"code": "CSC311H1", "title": "Introduction to Machine Learning", "units": 3.0}}', 'CS3244', 'CSC311H1', 'Machine Learning', 'Introduction to Machine Learning', NULL, 3.00, 'School of Computing', 1, 'repaired', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (58, 4, 25, '{"faculty": "School of Computing", "nus_course": {"code": "CS4218", "title": "Software Testing"}, "source_page": 1, "partner_course": {"code": "CSC410", "title": "Software Verification and Testing", "units": 0.5}}', 'CS4218', 'CSC410', 'Software Testing', 'Software Verification and Testing', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (59, 4, 26, '{"faculty": "School of Computing", "nus_course": {"code": "CS4212", "title": "Compiler Design"}, "source_page": 1, "partner_course": {"code": "CSC488", "title": "Compilers and Interpreters", "units": 3.0}}', 'CS4212', 'CSC488', 'Compiler Design', 'Compilers and Interpreters', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (60, 4, 27, '{"faculty": "School of Computing", "nus_course": {"code": "CS3221", "title": "Operating Systems Design"}, "source_page": 1, "partner_course": {"code": "CSC469", "title": "Operating Systems Design and Implementation", "units": 3.0}}', 'CS3221', 'CSC469', 'Operating Systems Design', 'Operating Systems Design and Implementation', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (61, 4, 28, '{"faculty": "School of Computing", "nus_course": {"code": "CS3210", "title": "Parallel Computing"}, "source_page": 1, "partner_course": {"code": "CSC367H1", "title": "Parallel Programming", "units": 3.0}}', 'CS3210', 'CSC367H1', 'Parallel Computing', 'Parallel Programming', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (62, 4, 29, '{"faculty": "School of Computing", "nus_course": {"code": "CS3243", "title": "Introduction to Artificial In"}, "source_page": 1, "partner_course": {"code": "MIE369H1", "title": "Introduction to Artificial Intelligence", "units": 0.5}}', 'CS3243', 'MIE369H1', 'Introduction to Artificial In', 'Introduction to Artificial Intelligence', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (63, 4, 30, '{"faculty": "School of Computing", "nus_course": {"code": "CS3243", "title": "Introduction to Artificial In"}, "source_page": 1, "partner_course": {"code": "ROB311H1", "title": "Artificial Intellgence", "units": 0.5}}', 'CS3243', 'ROB311H1', 'Introduction to Artificial In', 'Artificial Intellgence', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (64, 4, 31, '{"faculty": "School of Computing", "nus_course": {"code": "IS4226", "title": "Systematic Trading Strate"}, "source_page": 1, "partner_course": {"code": "RSM434", "title": "Financial Trading Strategies", "units": 0.5}}', 'IS4226', 'RSM434', 'Systematic Trading Strate', 'Financial Trading Strategies', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (65, 4, 32, '{"faculty": "School of Computing", "nus_course": {"code": "BT3102", "title": "Computational Methods fo"}, "source_page": 1, "partner_course": {"code": "ACT350", "title": "Applied Probability for Actuarial Science", "units": 0.5}}', 'BT3102', 'ACT350', 'Computational Methods fo', 'Applied Probability for Actuarial Science', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (66, 4, 33, '{"faculty": "School of Computing", "nus_course": {"code": "CS3230", "title": "Design and Analysis of Alg"}, "source_page": 1, "partner_course": {"code": "CSC373H1", "title": "Algorithm Design, Analysis & Complexity", "units": 0.5}}', 'CS3230', 'CSC373H1', 'Design and Analysis of Alg', 'Algorithm Design, Analysis & Complexity', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (67, 4, 34, '{"faculty": "School of Computing", "nus_course": {"code": "CS3243", "title": "Introduction to Artificial In"}, "source_page": 1, "partner_course": {"code": "CSC384H1", "title": "Introduction to Artificial Intelligence", "units": 0.5}}', 'CS3243', 'CSC384H1', 'Introduction to Artificial In', 'Introduction to Artificial Intelligence', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (68, 4, 35, '{"faculty": "School of Computing", "nus_course": {"code": "CS2102", "title": "Database Systems"}, "source_page": 1, "partner_course": {"code": "CSC343H1", "title": "Introduction to Databases", "units": 0.5}}', 'CS2102', 'CSC343H1', 'Database Systems', 'Introduction to Databases', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (69, 4, 36, '{"faculty": "School of Computing", "nus_course": {"code": "CS2104", "title": "Programming Language C"}, "source_page": 1, "partner_course": {"code": "CSC324H1", "title": "Principles of Programming Languages", "units": 0.5}}', 'CS2104', 'CSC324H1', 'Programming Language C', 'Principles of Programming Languages', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (70, 4, 37, '{"faculty": "School of Computing", "nus_course": {"code": "CS3230", "title": "Design and Analysis of Alg"}, "source_page": 1, "partner_course": {"code": "CSC373H", "title": "Algorithm Design and Analysis", "units": 0.5}}', 'CS3230', 'CSC373H', 'Design and Analysis of Alg', 'Algorithm Design and Analysis', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (71, 4, 38, '{"faculty": "School of Computing", "nus_course": {"code": "CS3241", "title": "Computer Graphics"}, "source_page": 1, "partner_course": {"code": "CSC317H1", "title": "Computer Graphics", "units": 0.5}}', 'CS3241', 'CSC317H1', 'Computer Graphics', 'Computer Graphics', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (72, 4, 39, '{"faculty": "School of Computing", "nus_course": {"code": "CS4248", "title": "Introduction to Large Lang"}, "source_page": 1, "partner_course": {"code": "CSC485H1", "title": "Computational Linguistics", "units": 0.5}}', 'CS4248', 'CSC485H1', 'Introduction to Large Lang', 'Computational Linguistics', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (73, 4, 40, '{"faculty": "School of Computing", "nus_course": {"code": "BT4240", "title": "Machine Learning for Pred"}, "source_page": 1, "partner_course": {"code": "APS360H1", "title": "Applied Fundamentals of Deep Learning", "units": 0.5}}', 'BT4240', 'APS360H1', 'Machine Learning for Pred', 'Applied Fundamentals of Deep Learning', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (74, 4, 41, '{"faculty": "School of Computing", "nus_course": {"code": "CS4211", "title": "Formal Methods for Softwa"}, "source_page": 1, "partner_course": {"code": "CSC465", "title": "Formal Methods in Software Design", "units": 0.5}}', 'CS4211', 'CSC465', 'Formal Methods for Softwa', 'Formal Methods in Software Design', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (75, 4, 42, '{"faculty": "School of Computing", "nus_course": {"code": "CS2105", "title": "Introduction to Computer"}, "source_page": 1, "partner_course": {"code": "CSC457H1", "title": "Principles of Computer Networks", "units": 0.5}}', 'CS2105', 'CSC457H1', 'Introduction to Computer', 'Principles of Computer Networks', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (76, 4, 43, '{"faculty": "School of Computing", "nus_course": {"code": "CS2103", "title": "Software Engineering"}, "source_page": 1, "partner_course": {"code": "CSC301H1", "title": "Introduction to Software Engineering", "units": 0.5}}', 'CS2103', 'CSC301H1', 'Software Engineering', 'Introduction to Software Engineering', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (77, 4, 44, '{"faculty": "School of Computing", "nus_course": {"code": "CS3244", "title": "Machine Learning"}, "source_page": 1, "partner_course": {"code": "CSC411H1", "title": "Machine Learning and Data Mining", "units": 0.5}}', 'CS3244', 'CSC411H1', 'Machine Learning', 'Machine Learning and Data Mining', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (78, 4, 45, '{"faculty": "School of Computing", "nus_course": {"code": "CS3244", "title": "Machine Learning"}, "source_page": 1, "partner_course": {"code": "ECE421", "title": "Introduction to Machine Learning", "units": 0.5}}', 'CS3244', 'ECE421', 'Machine Learning', 'Introduction to Machine Learning', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (79, 4, 46, '{"faculty": "School of Computing", "nus_course": {"code": "CS3243", "title": "Introduction to Artificial In"}, "source_page": 1, "partner_course": {"code": "ROB311", "title": "Artificial Intelligence", "units": 0.5}}', 'CS3243', 'ROB311', 'Introduction to Artificial In', 'Artificial Intelligence', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (80, 4, 47, '{"faculty": "School of Computing", "nus_course": {"code": "CS3244", "title": "Machine Learning"}, "source_page": 1, "partner_course": {"code": "ECE521", "title": "Inference Algorithms and Machine Learning", "units": 0.5}}', 'CS3244', 'ECE521', 'Machine Learning', 'Inference Algorithms and Machine Learning', NULL, 0.50, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (81, 4, 48, '{"faculty": "School of Computing", "nus_course": {"code": "Software Engineering", "title": null}, "source_page": 2, "partner_course": {"code": "CSC207H1", "title": "Software Design", "units": 0.5}}', 'Software Engineering', 'CSC207H1', NULL, 'Software Design', NULL, 0.50, 'School of Computing', 2, 'quarantined', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (82, 4, 49, '{"faculty": "School of Computing", "nus_course": {"code": "Discrete Structures", "title": null}, "source_page": 2, "partner_course": {"code": "CSC165H1", "title": "Mathematical Expression and Reasoning for Computer Science", "units": 0.5}}', 'Discrete Structures', 'CSC165H1', NULL, 'Mathematical Expression and Reasoning for Computer Science', NULL, 0.50, 'School of Computing', 2, 'quarantined', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (83, 4, 50, '{"faculty": "School of Computing", "nus_course": {"code": "Foundations of Machine Le", "title": null}, "source_page": 2, "partner_course": {"code": "CSCC11H3", "title": "Introduction to Machine Learning and Data Mining", "units": 0.5}}', 'Foundations of Machine Le', 'CSCC11H3', NULL, 'Introduction to Machine Learning and Data Mining', NULL, 0.50, 'School of Computing', 2, 'repaired', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (84, 4, 51, '{"faculty": "School of Computing", "nus_course": {"code": "Machine Learning for Pred", "title": null}, "source_page": 2, "partner_course": {"code": "MSE403H1", "title": "Data Sciences and Analytics for Materials Engineers", "units": 0.5}}', 'Machine Learning for Pred', 'MSE403H1', NULL, 'Data Sciences and Analytics for Materials Engineers', NULL, 0.50, 'School of Computing', 2, 'repaired', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (85, 4, 52, '{"faculty": "School of Computing", "nus_course": {"code": "Database Technology and", "title": null}, "source_page": 2, "partner_course": {"code": "CSC343H1", "title": "Introduction to Databases", "units": 0.5}}', 'Database Technology and', 'CSC343H1', NULL, 'Introduction to Databases', NULL, 0.50, 'School of Computing', 2, 'repaired', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (86, 4, 53, '{"faculty": "School of Computing", "nus_course": {"code": "Programming Methodology", "title": null}, "source_page": 2, "partner_course": {"code": "108H1F", "title": "Introduction to Computer Programming", "units": 0.5}}', 'Programming Methodology', '108H1F', NULL, 'Introduction to Computer Programming', NULL, 0.50, 'School of Computing', 2, 'quarantined', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (87, 4, 54, '{"faculty": "School of Computing", "nus_course": {"code": "Computer Organisation", "title": null}, "source_page": 2, "partner_course": {"code": "ECE243H1", "title": "Computer Organization", "units": 0.5}}', 'Computer Organisation', 'ECE243H1', NULL, 'Computer Organization', NULL, 0.50, 'School of Computing', 2, 'repaired', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (88, 5, 0, '{"faculty": "School of Computing", "nus_course": {"code": "CS2102", "title": "Database Systems"}, "source_page": 1, "partner_course": {"code": "ENG39098", "title": "Databases", "units": 2.0}}', 'CS2102', 'ENG39098', 'Database Systems', 'Databases', NULL, 2.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (89, 5, 1, '{"faculty": "School of Computing", "nus_course": {"code": "CS3243", "title": "Introduction to Artificial In"}, "source_page": 1, "partner_course": {"code": "ENG39116", "title": "Artificial Intelligence", "units": 2.0}}', 'CS3243', 'ENG39116', 'Introduction to Artificial In', 'Artificial Intelligence', NULL, 2.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (90, 5, 2, '{"faculty": "School of Computing", "nus_course": {"code": "CS4215", "title": "Programming Language Im"}, "source_page": 1, "partner_course": {"code": "ENG39128", "title": "Implementation of Programming Languages", "units": 2.0}}', 'CS4215', 'ENG39128', 'Programming Language Im', 'Implementation of Programming Languages', NULL, 2.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (92, 5, 4, '{"faculty": "School of Computing", "nus_course": {"code": "CS3244", "title": "Machine Learning"}, "source_page": 1, "partner_course": {"code": "T057001", "title": "Fundamentals of Artificial Intelligence- E2", "units": 2.0}}', 'CS3244', 'T057001', 'Machine Learning', 'Fundamentals of Artificial Intelligence- E2', NULL, 2.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (93, 5, 5, '{"faculty": "School of Computing", "nus_course": {"code": "CS2109S", "title": "Introduction to AI and Mac"}, "source_page": 1, "partner_course": {"code": "T57002", "title": "Fundamentals of Artificial Intelligence- E2", "units": 2.0}}', 'CS2109S', 'T57002', 'Introduction to AI and Mac', 'Fundamentals of Artificial Intelligence- E2', NULL, 2.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (94, 5, 6, '{"faculty": "School of Computing", "nus_course": {"code": "CS3231", "title": "Theory of Computation"}, "source_page": 1, "partner_course": {"code": "U-LAS30 20044 LE10", "title": "Introduction to Formal Languages-E2", "units": 2.0}}', 'CS3231', 'U-LAS30 20044 LE10', 'Theory of Computation', 'Introduction to Formal Languages-E2', NULL, 2.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (95, 6, 0, '{"faculty": "School of Computing", "nus_course": {"code": "CS1010E", "title": "Programming Methodology"}, "source_page": 1, "partner_course": {"code": "COSE101", "title": "Computer Programming I", "units": 3.0}}', 'CS1010E', 'COSE101', 'Programming Methodology', 'Computer Programming I', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (96, 6, 1, '{"faculty": "School of Computing", "nus_course": {"code": "BT1101", "title": "Introduction to Business A"}, "source_page": 1, "partner_course": {"code": "BUSS 216", "title": "Business Analytics I (English)", "units": 3.0}}', 'BT1101', 'BUSS 216', 'Introduction to Business A', 'Business Analytics I (English)', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (97, 6, 2, '{"faculty": "School of Computing", "nus_course": {"code": "CS1231", "title": "Discrete Structures"}, "source_page": 1, "partner_course": {"code": "COSE211", "title": "Discrete Mathematics", "units": 3.0}}', 'CS1231', 'COSE211', 'Discrete Structures', 'Discrete Mathematics', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (98, 6, 3, '{"faculty": "School of Computing", "nus_course": {"code": "CS2105", "title": "Introduction to Computer"}, "source_page": 1, "partner_course": {"code": "COSE 342", "title": "Computer Network", "units": 3.0}}', 'CS2105', 'COSE 342', 'Introduction to Computer', 'Computer Network', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (99, 6, 4, '{"faculty": "School of Computing", "nus_course": {"code": "CS3244", "title": "Machine Learning"}, "source_page": 1, "partner_course": {"code": "COSE 362", "title": "Machine Learning", "units": 3.0}}', 'CS3244', 'COSE 362', 'Machine Learning', 'Machine Learning', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (100, 6, 5, '{"faculty": "School of Computing", "nus_course": {"code": "CS2030", "title": "Programming Methodology"}, "source_page": 1, "partner_course": {"code": "KECE443", "title": "Object-Oriented Programming and Laboratory", "units": 3.0}}', 'CS2030', 'KECE443', 'Programming Methodology', 'Object-Oriented Programming and Laboratory', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (101, 6, 6, '{"faculty": "School of Computing", "nus_course": {"code": "CS2040C", "title": "Data Structures and Algor"}, "source_page": 1, "partner_course": {"code": "COSE 213", "title": "Data Structures", "units": 3.0}}', 'CS2040C', 'COSE 213', 'Data Structures and Algor', 'Data Structures', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (102, 6, 7, '{"faculty": "School of Computing", "nus_course": {"code": "CS2106", "title": "Introduction to Operating"}, "source_page": 1, "partner_course": {"code": "COSE341", "title": "Operating Systems", "units": 3.0}}', 'CS2106', 'COSE341', 'Introduction to Operating', 'Operating Systems', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (103, 6, 8, '{"faculty": "School of Computing", "nus_course": {"code": "CS3243", "title": "Introduction to Artificial In"}, "source_page": 1, "partner_course": {"code": "COSE361", "title": "Artificial Intelligence (English)", "units": 3.0}}', 'CS3243', 'COSE361', 'Introduction to Artificial In', 'Artificial Intelligence (English)', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (104, 6, 9, '{"faculty": "School of Computing", "nus_course": {"code": "IT2002", "title": "Database Technology and"}, "source_page": 1, "partner_course": {"code": "COSE371", "title": "Databases", "units": 3.0}}', 'IT2002', 'COSE371', 'Database Technology and', 'Databases', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (105, 6, 10, '{"faculty": "School of Computing", "nus_course": {"code": "CS5242", "title": "Neural Networks and Deep"}, "source_page": 1, "partner_course": {"code": "COSE474", "title": "Deep Learning", "units": 3.0}}', 'CS5242', 'COSE474', 'Neural Networks and Deep', 'Deep Learning', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (106, 6, 11, '{"faculty": "School of Computing", "nus_course": {"code": "CS3244", "title": "Machine Learning"}, "source_page": 1, "partner_course": {"code": "KECE345", "title": "\" MACHINE LEARNING AND INTELLIGENCE FOR ELECTRICAL ENGINEERS(English)\"", "units": 3.0}}', 'CS3244', 'KECE345', 'Machine Learning', '" MACHINE LEARNING AND INTELLIGENCE FOR ELECTRICAL ENGINEERS(English)"', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (107, 6, 12, '{"faculty": "School of Computing", "nus_course": {"code": "BT4240", "title": "Machine Learning for Pred"}, "source_page": 1, "partner_course": {"code": "BUSS217", "title": "Business Analytics II", "units": 3.0}}', 'BT4240', 'BUSS217', 'Machine Learning for Pred', 'Business Analytics II', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (108, 6, 13, '{"faculty": "School of Computing", "nus_course": {"code": "CS3236", "title": "Introduction to Informatio"}, "source_page": 1, "partner_course": {"code": "KECE421", "title": "INFORMATION AND CODING THEORY", "units": 3.0}}', 'CS3236', 'KECE421', 'Introduction to Informatio', 'INFORMATION AND CODING THEORY', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (109, 6, 14, '{"faculty": "School of Computing", "nus_course": {"code": "CS3230", "title": "Design and Analysis of Alg"}, "source_page": 1, "partner_course": {"code": "COSE214", "title": "ALORITHMS", "units": 3.0}}', 'CS3230', 'COSE214', 'Design and Analysis of Alg', 'ALORITHMS', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (110, 6, 15, '{"faculty": "School of Computing", "nus_course": {"code": "IS3150", "title": "Digital Media Marketing"}, "source_page": 1, "partner_course": {"code": "BUSS475", "title": "Internet Marketing", "units": 3.0}}', 'IS3150', 'BUSS475', 'Digital Media Marketing', 'Internet Marketing', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (111, 6, 16, '{"faculty": "School of Computing", "nus_course": {"code": "IS3103", "title": "Digital Transformation and"}, "source_page": 1, "partner_course": {"code": "COSE389", "title": "ENTREPRENEURSHIP & LEADERSHIP", "units": 3.0}}', 'IS3103', 'COSE389', 'Digital Transformation and', 'ENTREPRENEURSHIP & LEADERSHIP', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (112, 6, 17, '{"faculty": "School of Computing", "nus_course": {"code": "CS4248", "title": "Introduction to Large Lang"}, "source_page": 1, "partner_course": {"code": "COSE461", "title": "NATURAL LANGUAGE PROCESSING", "units": 3.0}}', 'CS4248', 'COSE461', 'Introduction to Large Lang', 'NATURAL LANGUAGE PROCESSING', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (113, 6, 18, '{"faculty": "School of Computing", "nus_course": {"code": "CS3231", "title": "Theory of Computation"}, "source_page": 1, "partner_course": {"code": "COSE215", "title": "THEORY OF COMPUTATION", "units": 3.0}}', 'CS3231', 'COSE215', 'Theory of Computation', 'THEORY OF COMPUTATION', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (114, 6, 19, '{"faculty": "School of Computing", "nus_course": {"code": "CS3241", "title": "Computer Graphics"}, "source_page": 1, "partner_course": {"code": "COSE331", "title": "COMPUTER GRAPHICS", "units": 3.0}}', 'CS3241', 'COSE331', 'Computer Graphics', 'COMPUTER GRAPHICS', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (115, 6, 20, '{"faculty": "School of Computing", "nus_course": {"code": "CS2104", "title": "Programming Language C"}, "source_page": 1, "partner_course": {"code": "COSE212", "title": "PROGRAMMING LANGUAGES", "units": 3.0}}', 'CS2104', 'COSE212', 'Programming Language C', 'PROGRAMMING LANGUAGES', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (116, 6, 21, '{"faculty": "School of Computing", "nus_course": {"code": "CS3244", "title": "Machine Learning"}, "source_page": 1, "partner_course": {"code": "BNCS411", "title": "INTRODUCTION TO BRAIN AND MACHINE LEARNING", "units": 3.0}}', 'CS3244', 'BNCS411', 'Machine Learning', 'INTRODUCTION TO BRAIN AND MACHINE LEARNING', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (117, 6, 22, '{"faculty": "School of Computing", "nus_course": {"code": "BT4240", "title": "Machine Learning for Pred"}, "source_page": 1, "partner_course": {"code": "BUSS316", "title": "Operations Analytics (English)", "units": 3.0}}', 'BT4240', 'BUSS316', 'Machine Learning for Pred', 'Operations Analytics (English)', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (118, 6, 23, '{"faculty": "School of Computing", "nus_course": {"code": "IS4246", "title": "Smart Systems and AI Go"}, "source_page": 1, "partner_course": {"code": "SMRT336", "title": "AI Security II (English)", "units": 3.0}}', 'IS4246', 'SMRT336', 'Smart Systems and AI Go', 'AI Security II (English)', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (119, 6, 24, '{"faculty": "School of Computing", "nus_course": {"code": "BT4221", "title": "Advanced Analytics with B"}, "source_page": 1, "partner_course": {"code": "STAT346", "title": "Statistical Data Science I (English)\"", "units": 3.0}}', 'BT4221', 'STAT346', 'Advanced Analytics with B', 'Statistical Data Science I (English)"', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (120, 6, 25, '{"faculty": "School of Computing", "nus_course": {"code": "IS4246", "title": "Smart Systems and AI Go"}, "source_page": 1, "partner_course": {"code": "BUSS305", "title": "Artificial Intelligence for Business (English)\"", "units": 3.0}}', 'IS4246', 'BUSS305', 'Smart Systems and AI Go', 'Artificial Intelligence for Business (English)"', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (121, 6, 26, '{"faculty": "School of Computing", "nus_course": {"code": "BT4222", "title": "Mining Web Data for Busin"}, "source_page": 1, "partner_course": {"code": "KHPM410", "title": "Data Science in Healthcare", "units": 3.0}}', 'BT4222', 'KHPM410', 'Mining Web Data for Busin', 'Data Science in Healthcare', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (122, 6, 27, '{"faculty": "School of Computing", "nus_course": {"code": "CS3240", "title": "Interaction Design"}, "source_page": 1, "partner_course": {"code": "COSE432", "title": "HUMAN COMPUTER INTERACTION", "units": 3.0}}', 'CS3240', 'COSE432', 'Interaction Design', 'HUMAN COMPUTER INTERACTION', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (123, 6, 28, '{"faculty": "School of Computing", "nus_course": {"code": "CS2105", "title": "Introduction to Computer"}, "source_page": 1, "partner_course": {"code": "COSE342", "title": "Computer Network", "units": 3.0}}', 'CS2105', 'COSE342', 'Introduction to Computer', 'Computer Network', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (124, 6, 29, '{"faculty": "School of Computing", "nus_course": {"code": "BT4222", "title": "Mining Web Data for Busin"}, "source_page": 1, "partner_course": {"code": "BUSS317", "title": "Social Media Analytics", "units": 3.0}}', 'BT4222', 'BUSS317', 'Mining Web Data for Busin', 'Social Media Analytics', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (125, 6, 30, '{"faculty": "School of Computing", "nus_course": {"code": "IS4261", "title": "Designing AI-driven Busin"}, "source_page": 1, "partner_course": {"code": "BUSS410", "title": "Technological Innovation Management: A Pre-requisite for Successful Entrepreneurship", "units": 3.0}}', 'IS4261', 'BUSS410', 'Designing AI-driven Busin', 'Technological Innovation Management: A Pre-requisite for Successful Entrepreneurship', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (126, 6, 31, '{"faculty": "School of Computing", "nus_course": {"code": "CS4222", "title": "Wireless Networking"}, "source_page": 1, "partner_course": {"code": "COSE442", "title": "Wireless Communications", "units": 3.0}}', 'CS4222', 'COSE442', 'Wireless Networking', 'Wireless Communications', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (127, 6, 32, '{"faculty": "School of Computing", "nus_course": {"code": "CS3241", "title": "Computer Graphics"}, "source_page": 1, "partner_course": {"code": "COSE436", "title": "Interactive Visualization", "units": 3.0}}', 'CS3241', 'COSE436', 'Computer Graphics', 'Interactive Visualization', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (128, 6, 33, '{"faculty": "School of Computing", "nus_course": {"code": "BT4240", "title": "Machine Learning for Pred"}, "source_page": 1, "partner_course": {"code": "KECE470", "title": "Pattern Recognition", "units": 3.0}}', 'BT4240', 'KECE470', 'Machine Learning for Pred', 'Pattern Recognition', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (129, 6, 34, '{"faculty": "School of Computing", "nus_course": {"code": "IS3103", "title": "Digital Transformation and"}, "source_page": 1, "partner_course": {"code": "BUSS215", "title": "INTRODUCTION TO MANAGEMENT INFORMATION SYSTEMS(English)", "units": 3.0}}', 'IS3103', 'BUSS215', 'Digital Transformation and', 'INTRODUCTION TO MANAGEMENT INFORMATION SYSTEMS(English)', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (130, 6, 35, '{"faculty": "School of Computing", "nus_course": {"code": "IS4241", "title": "Social Media Network Ana"}, "source_page": 1, "partner_course": {"code": "BUSS317", "title": "Social Media Analytics", "units": 3.0}}', 'IS4241', 'BUSS317', 'Social Media Network Ana', 'Social Media Analytics', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (131, 7, 0, '{"faculty": "School of Computing", "nus_course": {"code": "CS3244", "title": "Machine Learning"}, "source_page": 1, "partner_course": {"code": "CSI4120", "title": "MACHINE LEARNING", "units": 3.0}}', 'CS3244', 'CSI4120', 'Machine Learning', 'MACHINE LEARNING', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (132, 7, 1, '{"faculty": "School of Computing", "nus_course": {"code": "IT1244", "title": "Artificial Intelligence: Tech"}, "source_page": 1, "partner_course": {"code": "AIC2120", "title": "INTRODUCTION TO AI AND ITS APPLICATIONS", "units": 3.0}}', 'IT1244', 'AIC2120', 'Artificial Intelligence: Tech', 'INTRODUCTION TO AI AND ITS APPLICATIONS', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (133, 7, 2, '{"faculty": "School of Computing", "nus_course": {"code": "CS4243", "title": "Computer Vision and Patte"}, "source_page": 1, "partner_course": {"code": "CSI4116", "title": "Computer Vision", "units": 3.0}}', 'CS4243', 'CSI4116', 'Computer Vision and Patte', 'Computer Vision', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (134, 7, 3, '{"faculty": "School of Computing", "nus_course": {"code": "CS1231", "title": "Discrete Structures"}, "source_page": 1, "partner_course": {"code": "MAT2106", "title": "DISCRETE MATHEMATICS", "units": 3.0}}', 'CS1231', 'MAT2106', 'Discrete Structures', 'DISCRETE MATHEMATICS', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (135, 7, 4, '{"faculty": "School of Computing", "nus_course": {"code": "CS3243", "title": "Introduction to Artificial In"}, "source_page": 1, "partner_course": {"code": "CSI4108", "title": "Artificial Intelligence", "units": 3.0}}', 'CS3243', 'CSI4108', 'Introduction to Artificial In', 'Artificial Intelligence', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (136, 7, 5, '{"faculty": "School of Computing", "nus_course": {"code": "CS4243", "title": "Computer Vision and Patte"}, "source_page": 1, "partner_course": {"code": "CAS3116", "title": "COMPUTER VISION", "units": 3.0}}', 'CS4243', 'CAS3116', 'Computer Vision and Patte', 'COMPUTER VISION', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (137, 7, 6, '{"faculty": "School of Computing", "nus_course": {"code": "BT3104", "title": "Optimization Methods for"}, "source_page": 1, "partner_course": {"code": "STA4123", "title": "INTRODUCTION TO OPTIMIZATION FOR DATA SCIENCE", "units": 3.0}}', 'BT3104', 'STA4123', 'Optimization Methods for', 'INTRODUCTION TO OPTIMIZATION FOR DATA SCIENCE', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (138, 7, 7, '{"faculty": "School of Computing", "nus_course": {"code": "CS3244", "title": "Machine Learning"}, "source_page": 1, "partner_course": {"code": "CAS3120-01", "title": "MACHINE LEARNING", "units": 3.0}}', 'CS3244', 'CAS3120-01', 'Machine Learning', 'MACHINE LEARNING', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (139, 7, 8, '{"faculty": "School of Computing", "nus_course": {"code": "CS3231", "title": "Theory of Computation"}, "source_page": 1, "partner_course": {"code": "CSI3109", "title": "AUTOMATA AND FORMAL LANGUAGES", "units": 3.0}}', 'CS3231', 'CSI3109', 'Theory of Computation', 'AUTOMATA AND FORMAL LANGUAGES', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (140, 7, 9, '{"faculty": "School of Computing", "nus_course": {"code": "IS3103", "title": "Digital Transformation and"}, "source_page": 1, "partner_course": {"code": "BIZ3189-04", "title": "MANAGEMENT INFORMATION SYSTEMS", "units": 3.0}}', 'IS3103', 'BIZ3189-04', 'Digital Transformation and', 'MANAGEMENT INFORMATION SYSTEMS', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (141, 7, 10, '{"faculty": "School of Computing", "nus_course": {"code": "CS5242", "title": "Neural Networks and Deep"}, "source_page": 1, "partner_course": {"code": "EEE7501", "title": "NEURAL NETWORK", "units": 3.0}}', 'CS5242', 'EEE7501', 'Neural Networks and Deep', 'NEURAL NETWORK', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (142, 7, 11, '{"faculty": "School of Computing", "nus_course": {"code": "IS3103", "title": "Digital Transformation and"}, "source_page": 1, "partner_course": {"code": "ISM6011", "title": "Global IT Management", "units": 3.0}}', 'IS3103', 'ISM6011', 'Digital Transformation and', 'Global IT Management', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (143, 7, 12, '{"faculty": "School of Computing", "nus_course": {"code": "CS2105", "title": "Introduction to Computer"}, "source_page": 1, "partner_course": {"code": "CSI4106", "title": "Computer Networks", "units": 3.0}}', 'CS2105', 'CSI4106', 'Introduction to Computer', 'Computer Networks', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (144, 7, 13, '{"faculty": "School of Computing", "nus_course": {"code": "CS2105", "title": "Introduction to Computer"}, "source_page": 1, "partner_course": {"code": "EEE3450", "title": "COMMUNICATION NETWORKS", "units": 3.0}}', 'CS2105', 'EEE3450', 'Introduction to Computer', 'COMMUNICATION NETWORKS', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (145, 7, 14, '{"faculty": "School of Computing", "nus_course": {"code": "CS3244", "title": "Machine Learning"}, "source_page": 1, "partner_course": {"code": "EEE3314", "title": "INTRODUCTION ARTIFICIAL INTELLIGENCE", "units": 3.0}}', 'CS3244', 'EEE3314', 'Machine Learning', 'INTRODUCTION ARTIFICIAL INTELLIGENCE', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (146, 7, 15, '{"faculty": "School of Computing", "nus_course": {"code": "CS3244", "title": "Machine Learning"}, "source_page": 1, "partner_course": {"code": "STA3141", "title": "MATHEMATICS FOR MACHINE LEARNING", "units": 3.0}}', 'CS3244', 'STA3141', 'Machine Learning', 'MATHEMATICS FOR MACHINE LEARNING', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (147, 7, 16, '{"faculty": "School of Computing", "nus_course": {"code": "CS3244", "title": "Machine Learning"}, "source_page": 1, "partner_course": {"code": "STA3142", "title": "STATISTICAL MACHINE LEARNING", "units": 3.0}}', 'CS3244', 'STA3142', 'Machine Learning', 'STATISTICAL MACHINE LEARNING', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (148, 7, 17, '{"faculty": "School of Computing", "nus_course": {"code": "CS4222", "title": "Wireless Networking"}, "source_page": 1, "partner_course": {"code": "EE4624", "title": "WIRELESS AND MOBILE NETWORKS", "units": 3.0}}', 'CS4222', 'EE4624', 'Wireless Networking', 'WIRELESS AND MOBILE NETWORKS', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (149, 7, 18, '{"faculty": "School of Computing", "nus_course": {"code": "CS3263", "title": "Foundations of Artificial In"}, "source_page": 1, "partner_course": {"code": "EEE3314", "title": "INTRODUCTION ARTIFICIAL INTELLIGENCE", "units": 3.0}}', 'CS3263', 'EEE3314', 'Foundations of Artificial In', 'INTRODUCTION ARTIFICIAL INTELLIGENCE', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (150, 7, 19, '{"faculty": "School of Computing", "nus_course": {"code": "CS4268", "title": "Quantum Computing"}, "source_page": 1, "partner_course": {"code": "PHY4125", "title": "QUANTUM COMPUTER", "units": 3.0}}', 'CS4268', 'PHY4125', 'Quantum Computing', 'QUANTUM COMPUTER', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (151, 7, 20, '{"faculty": "School of Computing", "nus_course": {"code": "CS2040", "title": "Data Structures and Algor"}, "source_page": 1, "partner_course": {"code": "CSI2103", "title": "Data Structures", "units": 3.0}}', 'CS2040', 'CSI2103', 'Data Structures and Algor', 'Data Structures', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (152, 7, 21, '{"faculty": "School of Computing", "nus_course": {"code": "CS2107", "title": "Introduction to Informatio"}, "source_page": 1, "partner_course": {"code": "CSI4109", "title": "Information Security", "units": 3.0}}', 'CS2107', 'CSI4109', 'Introduction to Informatio', 'Information Security', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (153, 7, 22, '{"faculty": "School of Computing", "nus_course": {"code": "CS3264", "title": "Foundations of Machine Le"}, "source_page": 1, "partner_course": {"code": "STA3142", "title": "STATISTICAL MACHINE LEARNING", "units": 3.0}}', 'CS3264', 'STA3142', 'Foundations of Machine Le', 'STATISTICAL MACHINE LEARNING', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (154, 7, 23, '{"faculty": "School of Computing", "nus_course": {"code": "CS5242", "title": "Neural Networks and Deep"}, "source_page": 1, "partner_course": {"code": "STA9131", "title": "DEEP LEARNING FOR VISUAL RECOGNITION", "units": 3.0}}', 'CS5242', 'STA9131', 'Neural Networks and Deep', 'DEEP LEARNING FOR VISUAL RECOGNITION', NULL, 3.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_source_rows (id, snapshot_id, mapping_index, raw_json, source_nus_code, source_partner_code, source_nus_title, source_partner_title, source_nus_units, source_partner_units, source_faculty, source_page, outcome, created_at) OVERRIDING SYSTEM VALUE VALUES (155, 3, 32, '{"faculty": "School of Computing", "nus_course": {"code": "CS3213", "title": "Software Requirements Sp"}, "source_page": 1, "partner_course": {"code": "CITS3301", "title": "Software Requirements and Design", "units": 6.0}}', 'CS3213', 'CITS3301', 'Software Requirements Sp', 'Software Requirements and Design', NULL, 6.00, 'School of Computing', 1, 'accepted', '2026-10-23 23:01:41.084688+08');


--
-- Data for Name: catalog_issues; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (1, 1, 2, NULL, '/majors/2/electives/specialisations/AI Governance and Management', 'specialization_memberships_missing', 'warning', 'Source gives a note instead of an explicit membership list. Note: See official curriculum page for prescribed course list.', 'open', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (2, 1, 2, NULL, '/majors/2/electives/specialisations/Digital Product and Platform Management', 'specialization_memberships_missing', 'warning', 'Source gives a note instead of an explicit membership list. Note: See official curriculum page for prescribed course list.', 'open', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (3, 1, 2, NULL, '/majors/2/electives/specialisations/Financial Technology', 'specialization_memberships_missing', 'warning', 'Source gives a note instead of an explicit membership list. Note: See official curriculum page for prescribed course list.', 'open', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (4, 1, 2, NULL, '/majors/3/electives/focus_areas/0', 'focus_area_memberships_missing', 'warning', 'Source lists a focus-area name but no explicit course membership.', 'open', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (5, 1, 2, NULL, '/majors/3/electives/focus_areas/1', 'focus_area_memberships_missing', 'warning', 'Source lists a focus-area name but no explicit course membership.', 'open', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (6, 1, 2, NULL, '/majors/3/electives/focus_areas/2', 'focus_area_memberships_missing', 'warning', 'Source lists a focus-area name but no explicit course membership.', 'open', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (7, 1, 2, NULL, '/majors/3/electives/focus_areas/3', 'focus_area_memberships_missing', 'warning', 'Source lists a focus-area name but no explicit course membership.', 'open', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (8, 1, 2, NULL, '/majors/3/electives/focus_areas/4', 'focus_area_memberships_missing', 'warning', 'Source lists a focus-area name but no explicit course membership.', 'open', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (9, 1, 2, NULL, '/majors/3/electives/focus_areas/5', 'focus_area_memberships_missing', 'warning', 'Source lists a focus-area name but no explicit course membership.', 'open', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (10, 1, 2, NULL, '/majors/3/electives/focus_areas/6', 'focus_area_memberships_missing', 'warning', 'Source lists a focus-area name but no explicit course membership.', 'open', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (11, 1, 2, NULL, '/majors/3/electives/focus_areas/7', 'focus_area_memberships_missing', 'warning', 'Source lists a focus-area name but no explicit course membership.', 'open', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (12, 1, 2, NULL, '/majors/3/electives/focus_areas/8', 'focus_area_memberships_missing', 'warning', 'Source lists a focus-area name but no explicit course membership.', 'open', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (13, 1, 2, NULL, '/majors/3/electives/focus_areas/9', 'focus_area_memberships_missing', 'warning', 'Source lists a focus-area name but no explicit course membership.', 'open', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (14, 1, 2, NULL, '/majors/4/electives/specialisations/Digital Product and Platform Management', 'specialization_memberships_missing', 'warning', 'Source gives a note instead of an explicit membership list. Note: Optional; consult official specialisation list.', 'open', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (15, 1, 2, NULL, '/majors/4/electives/specialisations/Financial Technology', 'specialization_memberships_missing', 'warning', 'Source gives a note instead of an explicit membership list. Note: Optional; consult official specialisation list.', 'open', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (16, 1, 2, NULL, '/majors/4/electives/specialisations/Intelligent Systems Solutioning', 'specialization_memberships_missing', 'warning', 'Source gives a note instead of an explicit membership list. Note: Optional; consult official specialisation list.', 'open', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (17, 1, 4, 57, '/mappings/24/partner_course/units', 'partner_unit_conflict', 'error', 'Partner course units (''University of Toronto'', ''CSC311H1'') has conflicting value 3.0; first source value was 0.5.', 'resolved', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (18, 1, 4, 81, '/mappings/48', 'unresolved_repair', 'error', 'The row has an unresolved repair and stays quarantined.', 'quarantined', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (19, 1, 4, 81, '/mappings/48/nus_course/code', 'invalid_nus_code', 'error', 'NUS course code ''Software Engineering'' is not a valid course code.', 'quarantined', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (20, 1, 4, 81, '/mappings/48/nus_course/title', 'missing_nus_title', 'warning', 'NUS course title is missing or blank.', 'quarantined', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (21, 1, 4, 82, '/mappings/49', 'unresolved_repair', 'error', 'The row has an unresolved repair and stays quarantined.', 'quarantined', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (22, 1, 4, 82, '/mappings/49/nus_course/code', 'invalid_nus_code', 'error', 'NUS course code ''Discrete Structures'' is not a valid course code.', 'quarantined', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (23, 1, 4, 82, '/mappings/49/nus_course/title', 'missing_nus_title', 'warning', 'NUS course title is missing or blank.', 'quarantined', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (24, 1, 4, 83, '/mappings/50/nus_course/code', 'invalid_nus_code', 'error', 'NUS course code ''Foundations of Machine Le'' is not a valid course code.', 'resolved', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (25, 1, 4, 83, '/mappings/50/nus_course/title', 'missing_nus_title', 'warning', 'NUS course title is missing or blank.', 'resolved', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (26, 1, 4, 84, '/mappings/51/nus_course/code', 'invalid_nus_code', 'error', 'NUS course code ''Machine Learning for Pred'' is not a valid course code.', 'resolved', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (27, 1, 4, 84, '/mappings/51/nus_course/title', 'missing_nus_title', 'warning', 'NUS course title is missing or blank.', 'resolved', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (28, 1, 4, 85, '/mappings/52/nus_course/code', 'invalid_nus_code', 'error', 'NUS course code ''Database Technology and'' is not a valid course code.', 'resolved', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (29, 1, 4, 85, '/mappings/52/nus_course/title', 'missing_nus_title', 'warning', 'NUS course title is missing or blank.', 'resolved', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (30, 1, 4, 86, '/mappings/53', 'unresolved_repair', 'error', 'The row has an unresolved repair and stays quarantined.', 'quarantined', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (31, 1, 4, 86, '/mappings/53/nus_course/code', 'invalid_nus_code', 'error', 'NUS course code ''Programming Methodology'' is not a valid course code.', 'quarantined', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (32, 1, 4, 86, '/mappings/53/nus_course/title', 'missing_nus_title', 'warning', 'NUS course title is missing or blank.', 'quarantined', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (33, 1, 4, 87, '/mappings/54/nus_course/code', 'invalid_nus_code', 'error', 'NUS course code ''Computer Organisation'' is not a valid course code.', 'resolved', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_issues (id, batch_id, snapshot_id, source_row_id, json_pointer, issue_code, severity, message, status, created_at) OVERRIDING SYSTEM VALUE VALUES (34, 1, 4, 87, '/mappings/54/nus_course/title', 'missing_nus_title', 'warning', 'NUS course title is missing or blank.', 'resolved', '2026-10-23 23:01:40.872227+08');


--
-- Data for Name: catalog_repairs; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (1, 1, 4, 57, '/mappings/24/partner_course/units', '3.0', '0.5', 'https://artsci.calendar.utoronto.ca/course/csc311h1', 'CSC311H1 - Academic Calendar', '2026-10-22', '2026-27', 'CSC311H1: Introduction to Machine Learning ... Hours 24L/12T ... Previous Course Number CSC411H1', 'verified', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (2, 1, 4, 57, '/mappings/24/partner_course/units', '3.0', '0.5', 'https://engineering.calendar.utoronto.ca/electrical-and-computer-engineering-aeescbaser', 'Electrical and Computer Engineering', '2026-10-22', '2025-26', 'CSC311H1 : Introduction to Machine Learning F/S 2 - 1 0.50', 'verified', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (3, 1, 4, 81, '/mappings/48/nus_course/code', '"Software Engineering"', 'null', 'https://artsci.calendar.utoronto.ca/course/csc207h1', 'CSC207H1 - Academic Calendar', '2026-10-22', '2026-27', 'CSC207H1: Software Design ... An introduction to software design and development concepts, methods, and tools using a statically-typed object-oriented programming language such as Java.', 'unresolved', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (4, 1, 4, 81, '/mappings/48/nus_course/code', '"Software Engineering"', 'null', 'https://www.comp.nus.edu.sg/programmes/ug/focus/software', 'Software Engineering - NUS Computing', '2026-10-22', 'current programme page', 'CS2103 Software Engineering is the introductory course for this focus area (and a required course for all computer science students).', 'unresolved', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (5, 1, 4, 81, '/mappings/48/nus_course/code', '"Software Engineering"', 'null', 'https://www.nus.edu.sg/nusbulletin/ay202627/programmes/school-of-computing/undergraduate-education', 'Undergraduate Education - NUS Bulletin AY2026/27', '2026-10-22', 'AY2026/27', 'CS2103T Software Engineering | 4', 'unresolved', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (6, 1, 4, 81, '/mappings/48/nus_course/title', 'null', 'null', 'https://artsci.calendar.utoronto.ca/course/csc207h1', 'CSC207H1 - Academic Calendar', '2026-10-22', '2026-27', 'CSC207H1: Software Design ... An introduction to software design and development concepts, methods, and tools using a statically-typed object-oriented programming language such as Java.', 'unresolved', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (7, 1, 4, 81, '/mappings/48/nus_course/title', 'null', 'null', 'https://www.comp.nus.edu.sg/programmes/ug/focus/software', 'Software Engineering - NUS Computing', '2026-10-22', 'current programme page', 'CS2103 Software Engineering is the introductory course for this focus area (and a required course for all computer science students).', 'unresolved', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (8, 1, 4, 81, '/mappings/48/nus_course/title', 'null', 'null', 'https://www.nus.edu.sg/nusbulletin/ay202627/programmes/school-of-computing/undergraduate-education', 'Undergraduate Education - NUS Bulletin AY2026/27', '2026-10-22', 'AY2026/27', 'CS2103T Software Engineering | 4', 'unresolved', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (9, 1, 4, 82, '/mappings/49/nus_course/code', '"Discrete Structures"', 'null', 'https://artsci.calendar.utoronto.ca/course/csc165h1', 'CSC165H1 - Academic Calendar', '2026-10-22', '2026-27', 'CSC165H1: Mathematical Expression and Reasoning for Computer Science ... Introduction to abstraction and rigour.', 'unresolved', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (10, 1, 4, 82, '/mappings/49/nus_course/code', '"Discrete Structures"', 'null', 'https://www.comp.nus.edu.sg/programmes/ug/minorc/minor-in-ai', 'Minor in Artificial Intelligence - NUS Computing', '2026-10-22', 'current programme page', 'CS1231 Discrete Structures or MA1100/T Basic Discrete Mathematics', 'unresolved', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (11, 1, 4, 82, '/mappings/49/nus_course/code', '"Discrete Structures"', 'null', 'https://www.nus.edu.sg/nusbulletin/ay202627/programmes/school-of-computing/undergraduate-education', 'Undergraduate Education - NUS Bulletin AY2026/27', '2026-10-22', 'AY2026/27', 'CS1231S Discrete Structures | 4', 'unresolved', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (12, 1, 4, 82, '/mappings/49/nus_course/title', 'null', 'null', 'https://artsci.calendar.utoronto.ca/course/csc165h1', 'CSC165H1 - Academic Calendar', '2026-10-22', '2026-27', 'CSC165H1: Mathematical Expression and Reasoning for Computer Science ... Introduction to abstraction and rigour.', 'unresolved', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (13, 1, 4, 82, '/mappings/49/nus_course/title', 'null', 'null', 'https://www.comp.nus.edu.sg/programmes/ug/minorc/minor-in-ai', 'Minor in Artificial Intelligence - NUS Computing', '2026-10-22', 'current programme page', 'CS1231 Discrete Structures or MA1100/T Basic Discrete Mathematics', 'unresolved', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (14, 1, 4, 82, '/mappings/49/nus_course/title', 'null', 'null', 'https://www.nus.edu.sg/nusbulletin/ay202627/programmes/school-of-computing/undergraduate-education', 'Undergraduate Education - NUS Bulletin AY2026/27', '2026-10-22', 'AY2026/27', 'CS1231S Discrete Structures | 4', 'unresolved', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (15, 1, 4, 83, '/mappings/50/nus_course/code', '"Foundations of Machine Le"', '"CS3264"', 'https://utsc.calendar.utoronto.ca/course/cscc11h3', 'CSCC11H3 - UTSC Academic Calendar', '2026-10-22', 'current calendar', 'CSCC11H3: Introduction to Machine Learning and Data Mining', 'verified', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (16, 1, 4, 83, '/mappings/50/nus_course/code', '"Foundations of Machine Le"', '"CS3264"', 'https://www.comp.nus.edu.sg/programmes/ug/ai/curr/', 'Curriculum (Prospective Students) - Artificial Intelligence', '2026-10-22', 'AY2026/27', 'CS3264 Foundations of Machine Learning', 'verified', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (17, 1, 4, 83, '/mappings/50/nus_course/code', '"Foundations of Machine Le"', '"CS3264"', 'https://www.comp.nus.edu.sg/programmes/ug/minorc/minor-in-ai', 'Minor in Artificial Intelligence - NUS Computing', '2026-10-22', 'current programme page', 'CS3264 Foundations of Machine Learning', 'verified', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (18, 1, 4, 83, '/mappings/50/nus_course/title', 'null', '"Foundations of Machine Learning"', 'https://utsc.calendar.utoronto.ca/course/cscc11h3', 'CSCC11H3 - UTSC Academic Calendar', '2026-10-22', 'current calendar', 'CSCC11H3: Introduction to Machine Learning and Data Mining', 'verified', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (19, 1, 4, 83, '/mappings/50/nus_course/title', 'null', '"Foundations of Machine Learning"', 'https://www.comp.nus.edu.sg/programmes/ug/ai/curr/', 'Curriculum (Prospective Students) - Artificial Intelligence', '2026-10-22', 'AY2026/27', 'CS3264 Foundations of Machine Learning', 'verified', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (20, 1, 4, 83, '/mappings/50/nus_course/title', 'null', '"Foundations of Machine Learning"', 'https://www.comp.nus.edu.sg/programmes/ug/minorc/minor-in-ai', 'Minor in Artificial Intelligence - NUS Computing', '2026-10-22', 'current programme page', 'CS3264 Foundations of Machine Learning', 'verified', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (21, 1, 4, 84, '/mappings/51/nus_course/code', '"Machine Learning for Pred"', '"BT4240"', 'https://engineering.calendar.utoronto.ca/course/mse403h1', 'MSE403H1 - Faculty of Applied Science and Engineering', '2026-10-22', '2025-26', 'MSE403H1: Advanced A.I. for Accelerated Materials Discovery', 'verified', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (22, 1, 4, 84, '/mappings/51/nus_course/code', '"Machine Learning for Pred"', '"BT4240"', 'https://www.comp.nus.edu.sg/programmes/ug/ba', 'Bachelor of Science in Business Analytics', '2026-10-22', 'AY2026/27', 'BT4240 Machine Learning for Predictive Data Analytics', 'verified', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (23, 1, 4, 84, '/mappings/51/nus_course/title', 'null', '"Machine Learning for Predictive Data Analytics"', 'https://engineering.calendar.utoronto.ca/course/mse403h1', 'MSE403H1 - Faculty of Applied Science and Engineering', '2026-10-22', '2025-26', 'MSE403H1: Advanced A.I. for Accelerated Materials Discovery', 'verified', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (24, 1, 4, 84, '/mappings/51/nus_course/title', 'null', '"Machine Learning for Predictive Data Analytics"', 'https://www.comp.nus.edu.sg/programmes/ug/ba', 'Bachelor of Science in Business Analytics', '2026-10-22', 'AY2026/27', 'BT4240 Machine Learning for Predictive Data Analytics', 'verified', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (25, 1, 4, 85, '/mappings/52/nus_course/code', '"Database Technology and"', '"IT2002"', 'https://artsci.calendar.utoronto.ca/course/csc343h1', 'CSC343H1 - Academic Calendar', '2026-10-22', '2026-27', 'CSC343H1: Introduction to Databases ... Introduction to database management systems. The relational data model.', 'verified', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (26, 1, 4, 85, '/mappings/52/nus_course/code', '"Database Technology and"', '"IT2002"', 'https://cde.nus.edu.sg/ece/undergraduate/electrical-engineering/specialisations-and-minor/data-engineering', 'Minor in Data Engineering - Electrical and Computer Engineering', '2026-10-22', 'current programme page', 'IT2002 Database Technology and Management or CS2102 Database Systems', 'verified', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (27, 1, 4, 85, '/mappings/52/nus_course/code', '"Database Technology and"', '"IT2002"', 'https://cde.nus.edu.sg/isem/wp-content/uploads/sites/12/2026/06/Binder-BYOD1.pdf', 'Industrial and Systems Engineering specialisation requirements', '2026-10-22', 'AY2026/27', 'IT2002 Database Technology and Management or CS2102 Database Systems 4', 'verified', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (28, 1, 4, 85, '/mappings/52/nus_course/title', 'null', '"Database Technology and Management"', 'https://artsci.calendar.utoronto.ca/course/csc343h1', 'CSC343H1 - Academic Calendar', '2026-10-22', '2026-27', 'CSC343H1: Introduction to Databases ... Introduction to database management systems. The relational data model.', 'verified', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (29, 1, 4, 85, '/mappings/52/nus_course/title', 'null', '"Database Technology and Management"', 'https://cde.nus.edu.sg/ece/undergraduate/electrical-engineering/specialisations-and-minor/data-engineering', 'Minor in Data Engineering - Electrical and Computer Engineering', '2026-10-22', 'current programme page', 'IT2002 Database Technology and Management or CS2102 Database Systems', 'verified', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (30, 1, 4, 85, '/mappings/52/nus_course/title', 'null', '"Database Technology and Management"', 'https://cde.nus.edu.sg/isem/wp-content/uploads/sites/12/2026/06/Binder-BYOD1.pdf', 'Industrial and Systems Engineering specialisation requirements', '2026-10-22', 'AY2026/27', 'IT2002 Database Technology and Management or CS2102 Database Systems 4', 'verified', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (31, 1, 4, 86, '/mappings/53/nus_course/code', '"Programming Methodology"', 'null', 'https://artsci.calendar.utoronto.ca/course/csc108h1', 'CSC108H1 - Academic Calendar', '2026-10-22', '2026-27', 'CSC108H1: Introduction to Computer Programming ... Programming in a language such as Python.', 'unresolved', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (32, 1, 4, 86, '/mappings/53/nus_course/code', '"Programming Methodology"', 'null', 'https://cde.nus.edu.sg/me/wp-content/uploads/sites/11/2025/07/Sample-Schedule_RMI_AY2025-26-Onwards_20250624.pdf', 'Mechanical Engineering sample schedule', '2026-10-22', 'AY2025/26 onwards', 'CS1010E Programming Methodology 4', 'unresolved', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (33, 1, 4, 86, '/mappings/53/nus_course/code', '"Programming Methodology"', 'null', 'https://www.comp.nus.edu.sg/programmes/ug/cs/curr/', 'Curriculum (Prospective Students) - Computer Science', '2026-10-22', 'AY2026/27', 'CS1101S Programming Methodology

CS1010 Programming Methodology', 'unresolved', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (34, 1, 4, 86, '/mappings/53/nus_course/code', '"Programming Methodology"', 'null', 'https://www.comp.nus.edu.sg/programmes/ug/minorc/ba-minor', 'Minor in Business Analytics - NUS Computing', '2026-10-22', 'current programme page', 'CS1010S Programming Methodology', 'unresolved', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (35, 1, 4, 86, '/mappings/53/nus_course/title', 'null', 'null', 'https://artsci.calendar.utoronto.ca/course/csc108h1', 'CSC108H1 - Academic Calendar', '2026-10-22', '2026-27', 'CSC108H1: Introduction to Computer Programming ... Programming in a language such as Python.', 'unresolved', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (36, 1, 4, 86, '/mappings/53/nus_course/title', 'null', 'null', 'https://cde.nus.edu.sg/me/wp-content/uploads/sites/11/2025/07/Sample-Schedule_RMI_AY2025-26-Onwards_20250624.pdf', 'Mechanical Engineering sample schedule', '2026-10-22', 'AY2025/26 onwards', 'CS1010E Programming Methodology 4', 'unresolved', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (37, 1, 4, 86, '/mappings/53/nus_course/title', 'null', 'null', 'https://www.comp.nus.edu.sg/programmes/ug/cs/curr/', 'Curriculum (Prospective Students) - Computer Science', '2026-10-22', 'AY2026/27', 'CS1101S Programming Methodology

CS1010 Programming Methodology', 'unresolved', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (38, 1, 4, 86, '/mappings/53/nus_course/title', 'null', 'null', 'https://www.comp.nus.edu.sg/programmes/ug/minorc/ba-minor', 'Minor in Business Analytics - NUS Computing', '2026-10-22', 'current programme page', 'CS1010S Programming Methodology', 'unresolved', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (39, 1, 4, 87, '/mappings/54/nus_course/code', '"Computer Organisation"', '"CS2100"', 'https://engineering.calendar.utoronto.ca/course/ece243h1', 'ECE243H1 - Faculty of Applied Science and Engineering', '2026-10-22', '2025-26', 'ECE243H1: Computer Organization ... Basic computer structure. Design of central processing unit.', 'verified', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (40, 1, 4, 87, '/mappings/54/nus_course/code', '"Computer Organisation"', '"CS2100"', 'https://www.comp.nus.edu.sg/~cs2100/1_course_info/desc.html', 'CS2100 - Course Information - Description', '2026-10-22', 'AY2025/26 Semester 2', 'CS2100 Computer Organisation ... Units: 4', 'verified', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (41, 1, 4, 87, '/mappings/54/nus_course/code', '"Computer Organisation"', '"CS2100"', 'https://www.nus.edu.sg/nusbulletin/ay202627/programmes/school-of-computing/undergraduate-education', 'Undergraduate Education - NUS Bulletin AY2026/27', '2026-10-22', 'AY2026/27', 'CS2100 Computer Organisation | 4', 'verified', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (42, 1, 4, 87, '/mappings/54/nus_course/title', 'null', '"Computer Organisation"', 'https://engineering.calendar.utoronto.ca/course/ece243h1', 'ECE243H1 - Faculty of Applied Science and Engineering', '2026-10-22', '2025-26', 'ECE243H1: Computer Organization ... Basic computer structure. Design of central processing unit.', 'verified', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (43, 1, 4, 87, '/mappings/54/nus_course/title', 'null', '"Computer Organisation"', 'https://www.comp.nus.edu.sg/~cs2100/1_course_info/desc.html', 'CS2100 - Course Information - Description', '2026-10-22', 'AY2025/26 Semester 2', 'CS2100 Computer Organisation ... Units: 4', 'verified', '2026-10-23 23:01:40.872227+08');
INSERT INTO public.catalog_repairs (id, batch_id, snapshot_id, source_row_id, json_pointer, before_value, after_value, source_url, source_title, accessed_on, academic_year, evidence, status, created_at) OVERRIDING SYSTEM VALUE VALUES (44, 1, 4, 87, '/mappings/54/nus_course/title', 'null', '"Computer Organisation"', 'https://www.nus.edu.sg/nusbulletin/ay202627/programmes/school-of-computing/undergraduate-education', 'Undergraduate Education - NUS Bulletin AY2026/27', '2026-10-22', 'AY2026/27', 'CS2100 Computer Organisation | 4', 'verified', '2026-10-23 23:01:40.872227+08');


--
-- Data for Name: degrees; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.degrees (id, name, faculty, full_title, source_order) OVERRIDING SYSTEM VALUE VALUES (1, 'Artificial Intelligence', 'School of Computing', 'Bachelor of Computing (Artificial Intelligence)', 0);
INSERT INTO public.degrees (id, name, faculty, full_title, source_order) OVERRIDING SYSTEM VALUE VALUES (2, 'Business Analytics', 'School of Computing', 'Bachelor of Science (Business Analytics)', 1);
INSERT INTO public.degrees (id, name, faculty, full_title, source_order) OVERRIDING SYSTEM VALUE VALUES (3, 'Business Artificial Intelligence Systems', 'School of Computing', 'Bachelor of Computing (Business Artificial Intelligence Systems)', 2);
INSERT INTO public.degrees (id, name, faculty, full_title, source_order) OVERRIDING SYSTEM VALUE VALUES (4, 'Computer Science', 'School of Computing', 'Bachelor of Computing (Computer Science)', 3);
INSERT INTO public.degrees (id, name, faculty, full_title, source_order) OVERRIDING SYSTEM VALUE VALUES (5, 'Information Systems', 'School of Computing', 'Bachelor of Computing (Information Systems)', 4);
INSERT INTO public.degrees (id, name, faculty, full_title, source_order) OVERRIDING SYSTEM VALUE VALUES (6, 'Information Security', 'School of Computing', 'Bachelor of Computing (Information Security)', 5);


--
-- Data for Name: nus_modules; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('BT1101', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('BT2101', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('BT2102', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('BT3017', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('BT3102', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('BT3103', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('BT3104', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('BT4012', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('BT4013', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('BT4014', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('BT4015', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('BT4016', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('BT4101', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('BT4103', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('BT4211', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('BT4212', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('BT4221', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('BT4222', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('BT4240', 'Machine Learning for Predictive Data Analytics', NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('BT4241', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('BT4301', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CP3100', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CP3107', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CP3110', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CP3200', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CP3202', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CP3880', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CP4101', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS1010E', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS1231', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS1231S', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS2030', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS2030S', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS2040', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS2040C', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS2040S', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS2100', 'Computer Organisation', NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS2101', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS2102', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS2103', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS2103T', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS2104', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS2105', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS2106', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS2107', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS2109S', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS2251', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS3210', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS3213', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS3221', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS3230', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS3231', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS3235', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS3236', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS3237', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS3240', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS3241', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS3243', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS3244', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS3247', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS3263', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS3264', 'Foundations of Machine Learning', NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS3268', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS4211', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS4212', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS4215', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS4218', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS4220', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS4222', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS4225', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS4230', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS4236', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS4238', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS4239', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS4240', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS4243', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS4244', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS4246', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS4248', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS4249', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS4257', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS4261', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS4262', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS4268', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS4276', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS4277', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS4278', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS4347', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS5224', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS5231', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS5242', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS5321', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS5322', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS5331', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('CS5332', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('DBA4811', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IE3120', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IFS4101', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IFS4102', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IFS4103', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IFS4205', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS2101', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS2102', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS2103', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS2108', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS2109', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS3103', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS3106', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS3107', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS3108', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS3109', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS3150', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS3221', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS3240', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS3251', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS4010', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS4100', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS4103', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS4108', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS4151', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS4152', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS4204', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS4226', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS4228', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS4231', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS4233', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS4234', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS4236', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS4238', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS4241', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS4242', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS4243', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS4246', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS4248', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS4250', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS4261', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS4262', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS4301', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS4302', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS4303', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS4400', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS4401', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS4402', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IS4403', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IT1244', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('IT2002', 'Database Technology and Management', NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('MA1521', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('MA1522', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('MA4261', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('ST2334', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('ST4245', NULL, NULL, NULL);
INSERT INTO public.nus_modules (code, name, offering_faculty, verified_units) VALUES ('TR3202', NULL, NULL, NULL);


--
-- Data for Name: degree_modules; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (1, 'CS1231S', 'listed:required.mathematics_foundations');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (1, 'CS2030S', 'listed:required.computing_foundations');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (1, 'CS2040S', 'listed:required.computing_foundations');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (1, 'CS2101', 'listed:required.computing_foundations');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (1, 'CS2103T', 'listed:required.computing_foundations');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (1, 'CS2109S', 'listed:required.ai_foundations');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (1, 'CS2251', 'listed:required.mathematics_foundations');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (1, 'CS3230', 'listed:required.computing_foundations');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (1, 'CS3263', 'listed:required.ai_foundations');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (1, 'CS3264', 'listed:required.ai_foundations');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (1, 'CS3268', 'listed:required.ai_foundations');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (1, 'CS4220', 'choice:electives.ai_technical_electives_choose_min_12_units');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (1, 'CS4225', 'choice:electives.ai_technical_electives_choose_min_12_units');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (1, 'CS4240', 'choice:electives.ai_technical_electives_choose_min_12_units');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (1, 'CS4243', 'choice:required.perception_choose_one');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (1, 'CS4244', 'choice:electives.ai_technical_electives_choose_min_12_units');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (1, 'CS4246', 'choice:electives.ai_technical_electives_choose_min_12_units');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (1, 'CS4248', 'choice:required.perception_choose_one');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (1, 'CS4261', 'choice:electives.ai_technical_electives_choose_min_12_units');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (1, 'CS4262', 'choice:electives.ai_technical_electives_choose_min_12_units');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (1, 'CS4277', 'choice:electives.ai_technical_electives_choose_min_12_units');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (1, 'CS4278', 'choice:electives.ai_technical_electives_choose_min_12_units');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (1, 'CS4347', 'choice:electives.ai_technical_electives_choose_min_12_units');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (1, 'MA1521', 'listed:required.mathematics_foundations');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (1, 'MA1522', 'listed:required.mathematics_foundations');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (1, 'ST2334', 'listed:required.mathematics_foundations');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'BT2101', 'listed:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'BT2102', 'listed:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'BT3017', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.methodological_analytics; specialization:Machine Learning-based Analytics; specialization:Marketing Analytics');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'BT3102', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.methodological_analytics; specialization:Financial Analytics');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'BT3103', 'listed:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'BT3104', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.methodological_analytics');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'BT4012', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.methodological_analytics; specialization:Financial Analytics; specialization:Machine Learning-based Analytics');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'BT4013', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.business_applications; specialization:Financial Analytics');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'BT4014', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.digital_and_it; specialization:Machine Learning-based Analytics; specialization:Marketing Analytics');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'BT4015', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.methodological_analytics; specialization:Marketing Analytics');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'BT4016', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.business_applications; specialization:Financial Analytics');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'BT4101', 'choice:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'BT4103', 'listed:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'BT4211', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.business_applications; specialization:Marketing Analytics');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'BT4212', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.business_applications; specialization:Marketing Analytics');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'BT4221', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.methodological_analytics; specialization:Financial Analytics; specialization:Machine Learning-based Analytics');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'BT4222', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.methodological_analytics; specialization:Machine Learning-based Analytics; specialization:Marketing Analytics');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'BT4240', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.methodological_analytics; specialization:Machine Learning-based Analytics');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'BT4241', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.methodological_analytics; specialization:Machine Learning-based Analytics');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'BT4301', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.digital_and_it; specialization:Machine Learning-based Analytics');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'CP3100', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.methodological_analytics');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'CS2030', 'listed:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'CS2040', 'listed:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'CS3243', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.methodological_analytics; specialization:Machine Learning-based Analytics');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'CS3244', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.methodological_analytics');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'CS4248', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.methodological_analytics; specialization:Machine Learning-based Analytics');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'DBA4811', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.business_applications');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'IE3120', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.business_applications');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'IS2101', 'listed:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'IS3103', 'listed:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'IS3107', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.digital_and_it');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'IS3150', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.business_applications; specialization:Marketing Analytics');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'IS3221', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.digital_and_it');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'IS3240', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.business_applications');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'ST2334', 'listed:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'IS4226', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.digital_and_it; specialization:Financial Analytics');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'IS4228', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.digital_and_it; specialization:Financial Analytics');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'IS4234', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.digital_and_it; specialization:Financial Analytics');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'IS4241', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.business_applications; choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.methodological_analytics; specialization:Marketing Analytics');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'IS4242', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.business_applications');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'IS4246', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.digital_and_it; specialization:Machine Learning-based Analytics');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'IS4250', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.business_applications');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'IS4262', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.business_applications; specialization:Marketing Analytics');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'IS4302', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.digital_and_it; specialization:Financial Analytics');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'IS4303', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.digital_and_it; specialization:Financial Analytics');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'MA1521', 'listed:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'MA1522', 'listed:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'ST2334', 'listed:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (2, 'ST4245', 'choice:electives.programme_electives_choose_5_20_units_constraints_3_level_4000_min_3_bt_coded.methodological_analytics');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'BT2102', 'listed:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'BT3017', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'BT4014', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'BT4221', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'BT4301', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'CP3100', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'CP4101', 'choice:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'CS2030', 'listed:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'CS2040', 'listed:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'CS2105', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'CS2107', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IFS4101', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS2101', 'listed:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS2102', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS2108', 'listed:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS2109', 'listed:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS3103', 'listed:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS3107', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS3108', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS3109', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS3150', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS3221', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS3240', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS3251', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS4100', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS4108', 'listed:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS4151', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS4152', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS4226', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS4228', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS4231', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS4233', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS4234', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS4236', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS4238', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS4241', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS4243', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS4246', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS4248', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS4250', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS4261', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS4262', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS4301', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS4302', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS4303', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS4400', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS4401', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS4402', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'IS4403', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'MA1521', 'listed:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (3, 'MA1522', 'listed:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (4, 'CS1231S', 'listed:required.computer_science_foundation');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (4, 'CS2030S', 'listed:required.computer_science_foundation');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (4, 'CS2040S', 'listed:required.computer_science_foundation');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (4, 'CS2100', 'listed:required.computer_science_foundation');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (4, 'CS2101', 'listed:required.computer_science_foundation');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (4, 'CS2103T', 'listed:required.computer_science_foundation');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (4, 'CS2106', 'listed:required.computer_science_foundation');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (4, 'CS2109S', 'listed:required.computer_science_foundation');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (4, 'CS3230', 'listed:required.computer_science_foundation');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (4, 'MA1521', 'listed:required.mathematics_and_sciences');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (4, 'MA1522', 'listed:required.mathematics_and_sciences');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (4, 'ST2334', 'listed:required.mathematics_and_sciences');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'BT2102', 'choice:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'BT3017', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'BT4014', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'CP4101', 'choice:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'CS2030', 'listed:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'CS2040', 'listed:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'CS2102', 'choice:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'CS2105', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'CS2107', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'CS3240', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'CS3243', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IFS4101', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IS2101', 'listed:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IS2102', 'listed:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IS2103', 'listed:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IS3103', 'listed:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IS3106', 'listed:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IS3107', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IS3150', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IS3221', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IS3240', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IS3251', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IS4100', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IS4103', 'listed:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IS4151', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IS4152', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IS4226', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IS4228', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IS4231', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IS4233', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IS4234', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IS4236', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IS4238', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IS4241', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IS4242', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IS4243', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IS4246', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IS4248', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IS4250', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IS4261', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IS4262', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IS4301', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IS4302', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'IS4303', 'choice:electives.programme_electives_choose_5_20_units_at_least_3_level_4000');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'MA1521', 'listed:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (5, 'ST2334', 'listed:required.core');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'CP3107', 'listed:electives.industry_experience');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'CP3110', 'listed:electives.industry_experience');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'CP3200', 'listed:electives.industry_experience');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'CP3202', 'listed:electives.industry_experience');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'CP3880', 'listed:electives.industry_experience');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'CS1231S', 'listed:required.computing_foundation');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'CS2030', 'listed:required.computing_foundation');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'CS2040C', 'listed:required.computing_foundation');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'CS2100', 'listed:required.computing_foundation');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'CS2101', 'listed:required.computing_foundation');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'CS2103T', 'listed:required.computing_foundation');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'CS2105', 'listed:required.computing_foundation');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'CS2106', 'listed:required.computing_foundation');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'CS2107', 'listed:required.information_security');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'CS3235', 'listed:required.information_security');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'CS4230', 'choice:electives.information_security_electives_choose_8_units');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'CS4236', 'choice:electives.information_security_electives_choose_8_units');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'CS4238', 'choice:electives.information_security_electives_choose_8_units; choice:required.information_security');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'CS4239', 'choice:electives.information_security_electives_choose_8_units');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'CS4257', 'choice:electives.information_security_electives_choose_8_units');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'CS4276', 'choice:electives.information_security_electives_choose_8_units');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'CS5231', 'choice:electives.information_security_electives_choose_8_units');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'CS5321', 'choice:electives.information_security_electives_choose_8_units');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'CS5322', 'choice:electives.information_security_electives_choose_8_units');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'CS5331', 'choice:electives.information_security_electives_choose_8_units');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'CS5332', 'choice:electives.information_security_electives_choose_8_units');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'IFS4101', 'choice:electives.information_security_electives_choose_8_units');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'IFS4102', 'choice:electives.information_security_electives_choose_8_units');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'IFS4103', 'choice:electives.information_security_electives_choose_8_units; choice:required.information_security');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'IFS4205', 'choice:required.information_security');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'IS4010', 'listed:electives.industry_experience');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'IS4204', 'choice:electives.information_security_electives_choose_8_units');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'IS4231', 'listed:required.information_security');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'IS4233', 'choice:electives.information_security_electives_choose_8_units');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'IS4234', 'choice:electives.information_security_electives_choose_8_units');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'IS4238', 'choice:electives.information_security_electives_choose_8_units');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'IS4302', 'choice:electives.information_security_electives_choose_8_units');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'MA1521', 'listed:required.mathematics');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'MA1522', 'listed:required.mathematics');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'MA4261', 'choice:electives.information_security_electives_choose_8_units');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'ST2334', 'listed:required.mathematics');
INSERT INTO public.degree_modules (degree_id, module_code, requirement_type) VALUES (6, 'TR3202', 'listed:electives.industry_experience');


--
-- Data for Name: partner_universities; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.partner_universities (id, name, country, city, continent, source_order) OVERRIDING SYSTEM VALUE VALUES (1, 'University of Western Australia', 'Australia', NULL, NULL, 0);
INSERT INTO public.partner_universities (id, name, country, city, continent, source_order) OVERRIDING SYSTEM VALUE VALUES (2, 'University of Toronto', 'Canada', NULL, NULL, 1);
INSERT INTO public.partner_universities (id, name, country, city, continent, source_order) OVERRIDING SYSTEM VALUE VALUES (3, 'Kyoto University', 'Japan', NULL, NULL, 2);
INSERT INTO public.partner_universities (id, name, country, city, continent, source_order) OVERRIDING SYSTEM VALUE VALUES (4, 'Korea University', 'South Korea', NULL, NULL, 3);
INSERT INTO public.partner_universities (id, name, country, city, continent, source_order) OVERRIDING SYSTEM VALUE VALUES (5, 'Yonsei University', 'South Korea', NULL, NULL, 4);


--
-- Data for Name: pu_modules; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (1, 'BNCS411', 'INTRODUCTION TO BRAIN AND MACHINE LEARNING', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (2, 'BUSS 216', 'Business Analytics I (English)', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (3, 'BUSS215', 'INTRODUCTION TO MANAGEMENT INFORMATION SYSTEMS(English)', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (4, 'BUSS217', 'Business Analytics II', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (5, 'BUSS305', 'Artificial Intelligence for Business (English)"', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (6, 'BUSS316', 'Operations Analytics (English)', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (7, 'BUSS317', 'Social Media Analytics', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (8, 'BUSS410', 'Technological Innovation Management: A Pre-requisite for Successful Entrepreneurship', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (9, 'BUSS475', 'Internet Marketing', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (10, 'COSE 213', 'Data Structures', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (11, 'COSE 342', 'Computer Network', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (12, 'COSE 362', 'Machine Learning', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (13, 'COSE101', 'Computer Programming I', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (14, 'COSE211', 'Discrete Mathematics', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (15, 'COSE212', 'PROGRAMMING LANGUAGES', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (16, 'COSE214', 'ALORITHMS', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (17, 'COSE215', 'THEORY OF COMPUTATION', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (18, 'COSE331', 'COMPUTER GRAPHICS', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (19, 'COSE341', 'Operating Systems', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (20, 'COSE342', 'Computer Network', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (21, 'COSE361', 'Artificial Intelligence (English)', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (22, 'COSE371', 'Databases', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (23, 'COSE389', 'ENTREPRENEURSHIP & LEADERSHIP', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (24, 'COSE432', 'HUMAN COMPUTER INTERACTION', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (25, 'COSE436', 'Interactive Visualization', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (26, 'COSE442', 'Wireless Communications', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (27, 'COSE461', 'NATURAL LANGUAGE PROCESSING', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (28, 'COSE474', 'Deep Learning', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (29, 'KECE345', '" MACHINE LEARNING AND INTELLIGENCE FOR ELECTRICAL ENGINEERS(English)"', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (30, 'KECE421', 'INFORMATION AND CODING THEORY', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (31, 'KECE443', 'Object-Oriented Programming and Laboratory', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (32, 'KECE470', 'Pattern Recognition', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (33, 'KHPM410', 'Data Science in Healthcare', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (34, 'SMRT336', 'AI Security II (English)', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (35, 'STAT346', 'Statistical Data Science I (English)"', 4, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (36, 'ENG39098', 'Databases', 3, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (37, 'ENG39116', 'Artificial Intelligence', 3, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (38, 'ENG39128', 'Implementation of Programming Languages', 3, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (39, 'T019001', 'Information Network-E2', 3, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (40, 'T057001', 'Fundamentals of Artificial Intelligence- E2', 3, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (41, 'T57002', 'Fundamentals of Artificial Intelligence- E2', 3, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (42, 'U-LAS30 20044 LE10', 'Introduction to Formal Languages-E2', 3, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (43, 'ACT350', 'Applied Probability for Actuarial Science', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (44, 'APS360H1', 'Applied Fundamentals of Deep Learning', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (45, 'BCB420H1', 'Computational Systems Biology', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (46, 'CSC301H1', 'Introduction to Software Engineering', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (47, 'CSC302H1', 'Engineering Large Software Systems', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (48, 'CSC309H1', 'Programming on the Web', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (49, 'CSC311H1', 'Introduction to Machine Learning', 2, 0.50);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (50, 'CSC317H1', 'Computer Graphics', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (51, 'CSC322H5', 'Introduction to Algebraic Cryptography', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (52, 'CSC324H1', 'Principles of Programming Languages', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (53, 'CSC326H1', 'Programming Languages', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (54, 'CSC343H1', 'Introduction to Databases', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (55, 'CSC3465H1', 'Formal Methods in Software Design', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (56, 'CSC358H1', 'Principles of Computer Networks', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (57, 'CSC367H1', 'Parallel Programming', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (58, 'CSC369H1', 'Operating Systems', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (59, 'CSC373H', 'Algorithm Design and Analysis', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (60, 'CSC373H1', 'Algorithm Design, Analysis & Complexity', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (61, 'CSC384H1', 'Introduction to Artificial Intelligence', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (62, 'CSC401H1', 'Natural Language Computing', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (63, 'CSC404H1', 'Introduction to Video Game Design', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (64, 'CSC410', 'Software Verification and Testing', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (65, 'CSC411H1', 'Machine Learning and Data Mining', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (66, 'CSC412', 'Probabilistic Learning and Reasoning', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (67, 'CSC413H1', '" Neural Networks and Deep Learning"', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (68, 'CSC420H1', 'Introduction to Image Understanding', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (69, 'CSC428H1-S', 'Human-Computer Interaction', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (70, 'CSC443H1', 'Database System Technology', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (71, 'CSC444H1', 'Software Engineering', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (72, 'CSC457H1', 'Principles of Computer Networks', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (73, 'CSC465', 'Formal Methods in Software Design', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (74, 'CSC469', 'Operating Systems Design and Implementation', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (75, 'CSC485H1', 'Computational Linguistics', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (76, 'CSC488', 'Compilers and Interpreters', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (77, 'CSCC11H3', 'Introduction to Machine Learning and Data Mining', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (78, 'ECE243H1', 'Computer Organization', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (79, 'ECE344H1', 'Operating Systems', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (80, 'ECE352', 'Computer Organization', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (81, 'ECE358', 'Foundations of Computing', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (82, 'ECE421', 'Introduction to Machine Learning', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (83, 'ECE521', 'Inference Algorithms and Machine Learning', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (84, 'ECE568H1', 'Computer Security', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (85, 'ECO375H1', 'Foundations of Econometrics', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (86, 'MIE369H1', 'Introduction to Artificial Intelligence', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (87, 'MSE403H1', 'Data Sciences and Analytics for Materials Engineers', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (88, 'ROB311', 'Artificial Intelligence', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (89, 'ROB311H1', 'Artificial Intellgence', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (90, 'ROB313H1', 'Introduction to Learning from Data', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (91, 'RSM434', 'Financial Trading Strategies', 2, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (92, 'BUSN5001', 'Blockchain and Distributed Ledger Technologies in Business', 1, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (93, 'CITS1402', 'Relational Database Management Systems', 1, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (94, 'CITS2200', 'Data Structures and Algorithms', 1, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (95, 'CITS3001', 'Algorithms, Agents and Artificial Intelligence', 1, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (96, 'CITS3002', 'Computer Networks', 1, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (97, 'CITS3004', 'Cybersecurity', 1, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (98, 'CITS3006', 'Penetration Testing', 1, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (99, 'CITS3007', 'Secure Coding', 1, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (100, 'CITS3301', 'Software Requirements and Design', 1, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (101, 'CITS4009', 'Computational Data Analysis', 1, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (102, 'CITS4404', 'Artificial Intelligence and Adaptive Systems', 1, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (103, 'CITS4419', 'Mobile and Wireless Computing', 1, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (104, 'CITS5503', 'Cloud Computing', 1, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (105, 'CITS5506', 'The Internet of Things', 1, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (106, 'CITS5507', 'High Performance Computing', 1, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (107, 'CTIS2005', 'Object Oriented Programming', 1, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (108, 'ENVT4411', 'Geographic Information Systems Applications', 1, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (109, 'ENVT5566', 'Advanced Spatial and Environmental Modelling', 1, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (110, 'FINA4491', 'Capital Markets Research', 1, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (111, 'GEOG2201', 'Geographic Information Systems', 1, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (112, 'GEOG3300', 'Advanced Spatial Analysis', 1, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (113, 'MATH3002', 'Network Science', 1, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (114, 'MKTG2305', 'Marketing Research', 1, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (115, 'MKTG3307', 'Digital Marketing', 1, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (116, 'MKTG3308', 'Marketing Analytics', 1, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (117, 'MKTG5504', 'Big Data in Marketing', 1, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (118, 'STAT3063', 'Spatial Statistics and Modeling', 1, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (119, 'STAT3406', 'Applied Statistics and Data Visualisation', 1, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (120, 'STAT4064', 'Applied Predictive Modeling', 1, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (121, 'AIC2120', 'INTRODUCTION TO AI AND ITS APPLICATIONS', 5, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (122, 'BIZ3189-04', 'MANAGEMENT INFORMATION SYSTEMS', 5, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (123, 'CAS3116', 'COMPUTER VISION', 5, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (124, 'CAS3120-01', 'MACHINE LEARNING', 5, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (125, 'CSI2103', 'Data Structures', 5, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (126, 'CSI3109', 'AUTOMATA AND FORMAL LANGUAGES', 5, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (127, 'CSI4106', 'Computer Networks', 5, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (128, 'CSI4108', 'Artificial Intelligence', 5, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (129, 'CSI4109', 'Information Security', 5, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (130, 'CSI4116', 'Computer Vision', 5, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (131, 'CSI4120', 'MACHINE LEARNING', 5, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (132, 'EE4624', 'WIRELESS AND MOBILE NETWORKS', 5, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (133, 'EEE3314', 'INTRODUCTION ARTIFICIAL INTELLIGENCE', 5, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (134, 'EEE3450', 'COMMUNICATION NETWORKS', 5, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (135, 'EEE7501', 'NEURAL NETWORK', 5, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (136, 'ISM6011', 'Global IT Management', 5, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (137, 'MAT2106', 'DISCRETE MATHEMATICS', 5, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (138, 'PHY4125', 'QUANTUM COMPUTER', 5, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (139, 'STA3141', 'MATHEMATICS FOR MACHINE LEARNING', 5, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (140, 'STA3142', 'STATISTICAL MACHINE LEARNING', 5, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (141, 'STA4123', 'INTRODUCTION TO OPTIMIZATION FOR DATA SCIENCE', 5, NULL);
INSERT INTO public.pu_modules (id, code, name, partner_university_id, verified_units) OVERRIDING SYSTEM VALUE VALUES (142, 'STA9131', 'DEEP LEARNING FOR VISUAL RECOGNITION', 5, NULL);


--
-- Data for Name: module_mappings; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (1, 'IS4302', 92, 1, 0, 'Blockchain and Distributed', NULL, 'Blockchain and Distributed Ledger Technologies in Business', 6.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (2, 'CS2102', 93, 2, 1, 'Database Systems', NULL, 'Relational Database Management Systems', 6.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (3, 'CS2040', 94, 3, 2, 'Data Structures and Algor', NULL, 'Data Structures and Algorithms', 6.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (4, 'BT4014', 95, 4, 3, 'Analytics Driven Design of', NULL, 'Algorithms, Agents and Artificial Intelligence', 6.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (5, 'CS3243', 95, 5, 4, 'Introduction to Artificial In', NULL, 'Algorithms, Agents and Artificial Intelligence', 6.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (6, 'CS2105', 96, 6, 5, 'Introduction to Computer', NULL, 'Computer Networks', 6.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (7, 'CS3235', 97, 7, 6, 'Computer Security', NULL, 'Cybersecurity', 6.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (8, 'IFS4103', 98, 8, 7, 'Penetration Testing Practic', NULL, 'Penetration Testing', 6.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (9, 'CS4239', 99, 9, 8, 'Software Security', NULL, 'Secure Coding', 6.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (10, 'CS3213', 100, 10, 9, 'Software Requirements Sp', NULL, 'Software Requirements and Design', 6.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (11, 'BT4014', 101, 11, 10, 'Analytics Driven Design of', NULL, 'Computational Data Analysis', 6.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (12, 'BT4014', 102, 12, 11, 'Analytics Driven Design of', NULL, 'Artificial Intelligence and Adaptive Systems', 6.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (13, 'CS3243', 102, 13, 12, 'Introduction to Artificial In', NULL, 'Artificial Intelligence and Adaptive Systems', 6.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (14, 'IS4242', 102, 14, 13, 'Intelligent Systems and Te', NULL, 'Artificial Intelligence and Adaptive Systems', 6.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (15, 'CS4222', 103, 15, 14, 'Wireless Networking', NULL, 'Mobile and Wireless Computing', 6.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (16, 'CS5224', 104, 16, 15, 'Cloud Computing', NULL, 'Cloud Computing', 6.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (17, 'CS3237', 105, 17, 16, 'Introduction to Internet of', NULL, 'The Internet of Things', 6.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (18, 'CS3210', 106, 18, 17, 'Parallel Computing', NULL, 'High Performance Computing', 6.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (19, 'CS2030', 107, 19, 18, 'Programming Methodology', NULL, 'Object Oriented Programming', 6.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (20, 'BT4015', 108, 20, 19, 'Geospatial Analytics', NULL, 'Geographic Information Systems Applications', 6.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (21, 'BT4015', 109, 21, 20, 'Geospatial Analytics', NULL, 'Advanced Spatial and Environmental Modelling', 6.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (22, 'BT4013', 110, 22, 21, 'Analytics for Capital Marke', NULL, 'Capital Markets Research', 6.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (23, 'BT4015', 111, 23, 22, 'Geospatial Analytics', NULL, 'Geographic Information Systems', 6.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (24, 'BT4015', 112, 24, 23, 'Geospatial Analytics', NULL, 'Advanced Spatial Analysis', 6.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (25, 'IS4241', 113, 25, 24, 'Social Media Network Ana', NULL, 'Network Science', 6.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (26, 'BT4211', 114, 26, 25, 'Data-Driven Marketing', NULL, 'Marketing Research', 6.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (27, 'BT4211', 115, 27, 26, 'Data-Driven Marketing', NULL, 'Digital Marketing', 6.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (28, 'BT4211', 116, 28, 27, 'Data-Driven Marketing', NULL, 'Marketing Analytics', 6.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (29, 'BT4211', 117, 29, 28, 'Data-Driven Marketing', NULL, 'Big Data in Marketing', 6.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (30, 'BT4015', 118, 30, 29, 'Geospatial Analytics', NULL, 'Spatial Statistics and Modeling', 6.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (31, 'BT4240', 119, 31, 30, 'Machine Learning for Pred', NULL, 'Applied Statistics and Data Visualisation', 6.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (32, 'BT4240', 120, 32, 31, 'Machine Learning for Pred', NULL, 'Applied Predictive Modeling', 6.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (33, 'CS2106', 79, 33, 32, 'Introduction to Operating', NULL, 'Operating Systems', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (34, 'CS2103', 71, 34, 33, 'Software Engineering', NULL, 'Software Engineering', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (35, 'CS2104', 53, 35, 34, 'Programming Language C', NULL, 'Programming Languages', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (36, 'CS3247', 63, 36, 35, 'Game Development', NULL, 'Introduction to Video Game Design', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (37, 'CS3244', 90, 37, 36, 'Machine Learning', NULL, 'Introduction to Learning from Data', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (38, 'CS4249', 69, 38, 37, 'Quantitative Methods of H', NULL, 'Human-Computer Interaction', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (39, 'CS4243', 68, 39, 38, 'Computer Vision and Patte', NULL, 'Introduction to Image Understanding', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (40, 'CS5242', 67, 40, 39, 'Neural Networks and Deep', NULL, '" Neural Networks and Deep Learning"', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (41, 'BT3103', 48, 41, 40, 'Application Systems Deve', NULL, 'Programming on the Web', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (42, 'BT3102', 66, 42, 41, 'Computational Methods fo', NULL, 'Probabilistic Learning and Reasoning', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (43, 'IS3107', 70, 43, 42, 'Data Engineering', NULL, 'Database System Technology', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (44, 'CS3264', 49, 44, 43, 'Foundations of Machine Le', NULL, 'Introduction to Machine Learning', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (45, 'CS4248', 62, 45, 44, 'Introduction to Large Lang', NULL, 'Natural Language Computing', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (46, 'CS3213', 47, 46, 45, 'Software Requirements Sp', NULL, 'Engineering Large Software Systems', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (47, 'CS3263', 61, 47, 46, 'Foundations of Artificial In', NULL, 'Introduction to Artificial Intelligence', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (48, 'CS4211', 55, 48, 47, 'Formal Methods for Softwa', NULL, 'Formal Methods in Software Design', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (49, 'CS2106', 58, 49, 48, 'Introduction to Operating', NULL, 'Operating Systems', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (50, 'BT2101', 85, 50, 49, 'Econometrics Modeling for', NULL, 'Foundations of Econometrics', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (51, 'CS4220', 45, 51, 50, 'Knowledge Discovery Meth', NULL, 'Computational Systems Biology', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (52, 'CS2100', 80, 52, 51, 'Computer Organisation', NULL, 'Computer Organization', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (53, 'CS3230', 81, 53, 52, 'Design and Analysis of Alg', NULL, 'Foundations of Computing', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (54, 'CS4236', 51, 54, 53, 'Cryptography in Practice:', NULL, 'Introduction to Algebraic Cryptography', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (55, 'CS2105', 56, 55, 54, 'Introduction to Computer', NULL, 'Principles of Computer Networks', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (56, 'CS3235', 84, 56, 55, 'Computer Security', NULL, 'Computer Security', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (57, 'CS3244', 49, 57, 56, 'Machine Learning', NULL, 'Introduction to Machine Learning', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (58, 'CS4218', 64, 58, 57, 'Software Testing', NULL, 'Software Verification and Testing', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (59, 'CS4212', 76, 59, 58, 'Compiler Design', NULL, 'Compilers and Interpreters', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (60, 'CS3221', 74, 60, 59, 'Operating Systems Design', NULL, 'Operating Systems Design and Implementation', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (61, 'CS3210', 57, 61, 60, 'Parallel Computing', NULL, 'Parallel Programming', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (62, 'CS3243', 86, 62, 61, 'Introduction to Artificial In', NULL, 'Introduction to Artificial Intelligence', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (63, 'CS3243', 89, 63, 62, 'Introduction to Artificial In', NULL, 'Artificial Intellgence', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (64, 'IS4226', 91, 64, 63, 'Systematic Trading Strate', NULL, 'Financial Trading Strategies', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (65, 'BT3102', 43, 65, 64, 'Computational Methods fo', NULL, 'Applied Probability for Actuarial Science', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (66, 'CS3230', 60, 66, 65, 'Design and Analysis of Alg', NULL, 'Algorithm Design, Analysis & Complexity', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (67, 'CS3243', 61, 67, 66, 'Introduction to Artificial In', NULL, 'Introduction to Artificial Intelligence', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (68, 'CS2102', 54, 68, 67, 'Database Systems', NULL, 'Introduction to Databases', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (69, 'CS2104', 52, 69, 68, 'Programming Language C', NULL, 'Principles of Programming Languages', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (70, 'CS3230', 59, 70, 69, 'Design and Analysis of Alg', NULL, 'Algorithm Design and Analysis', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (71, 'CS3241', 50, 71, 70, 'Computer Graphics', NULL, 'Computer Graphics', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (72, 'CS4248', 75, 72, 71, 'Introduction to Large Lang', NULL, 'Computational Linguistics', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (73, 'BT4240', 44, 73, 72, 'Machine Learning for Pred', NULL, 'Applied Fundamentals of Deep Learning', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (74, 'CS4211', 73, 74, 73, 'Formal Methods for Softwa', NULL, 'Formal Methods in Software Design', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (75, 'CS2105', 72, 75, 74, 'Introduction to Computer', NULL, 'Principles of Computer Networks', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (76, 'CS2103', 46, 76, 75, 'Software Engineering', NULL, 'Introduction to Software Engineering', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (77, 'CS3244', 65, 77, 76, 'Machine Learning', NULL, 'Machine Learning and Data Mining', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (78, 'CS3244', 82, 78, 77, 'Machine Learning', NULL, 'Introduction to Machine Learning', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (79, 'CS3243', 88, 79, 78, 'Introduction to Artificial In', NULL, 'Artificial Intelligence', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (80, 'CS3244', 83, 80, 79, 'Machine Learning', NULL, 'Inference Algorithms and Machine Learning', 0.50, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (81, 'CS3264', 77, 83, 82, 'Foundations of Machine Learning', NULL, 'Introduction to Machine Learning and Data Mining', 0.50, 'School of Computing', 2);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (82, 'BT4240', 87, 84, 83, 'Machine Learning for Predictive Data Analytics', NULL, 'Data Sciences and Analytics for Materials Engineers', 0.50, 'School of Computing', 2);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (83, 'IT2002', 54, 85, 84, 'Database Technology and Management', NULL, 'Introduction to Databases', 0.50, 'School of Computing', 2);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (84, 'CS2100', 78, 87, 86, 'Computer Organisation', NULL, 'Computer Organization', 0.50, 'School of Computing', 2);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (85, 'CS2102', 36, 88, 87, 'Database Systems', NULL, 'Databases', 2.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (86, 'CS3243', 37, 89, 88, 'Introduction to Artificial In', NULL, 'Artificial Intelligence', 2.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (87, 'CS4215', 38, 90, 89, 'Programming Language Im', NULL, 'Implementation of Programming Languages', 2.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (88, 'CS2105', 39, 91, 90, 'Introduction to Computer', NULL, 'Information Network-E2', 2.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (89, 'CS3244', 40, 92, 91, 'Machine Learning', NULL, 'Fundamentals of Artificial Intelligence- E2', 2.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (90, 'CS2109S', 41, 93, 92, 'Introduction to AI and Mac', NULL, 'Fundamentals of Artificial Intelligence- E2', 2.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (91, 'CS3231', 42, 94, 93, 'Theory of Computation', NULL, 'Introduction to Formal Languages-E2', 2.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (92, 'CS1010E', 13, 95, 94, 'Programming Methodology', NULL, 'Computer Programming I', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (93, 'BT1101', 2, 96, 95, 'Introduction to Business A', NULL, 'Business Analytics I (English)', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (94, 'CS1231', 14, 97, 96, 'Discrete Structures', NULL, 'Discrete Mathematics', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (95, 'CS2105', 11, 98, 97, 'Introduction to Computer', NULL, 'Computer Network', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (96, 'CS3244', 12, 99, 98, 'Machine Learning', NULL, 'Machine Learning', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (97, 'CS2030', 31, 100, 99, 'Programming Methodology', NULL, 'Object-Oriented Programming and Laboratory', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (98, 'CS2040C', 10, 101, 100, 'Data Structures and Algor', NULL, 'Data Structures', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (99, 'CS2106', 19, 102, 101, 'Introduction to Operating', NULL, 'Operating Systems', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (100, 'CS3243', 21, 103, 102, 'Introduction to Artificial In', NULL, 'Artificial Intelligence (English)', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (101, 'IT2002', 22, 104, 103, 'Database Technology and', NULL, 'Databases', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (102, 'CS5242', 28, 105, 104, 'Neural Networks and Deep', NULL, 'Deep Learning', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (103, 'CS3244', 29, 106, 105, 'Machine Learning', NULL, '" MACHINE LEARNING AND INTELLIGENCE FOR ELECTRICAL ENGINEERS(English)"', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (104, 'BT4240', 4, 107, 106, 'Machine Learning for Pred', NULL, 'Business Analytics II', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (105, 'CS3236', 30, 108, 107, 'Introduction to Informatio', NULL, 'INFORMATION AND CODING THEORY', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (106, 'CS3230', 16, 109, 108, 'Design and Analysis of Alg', NULL, 'ALORITHMS', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (107, 'IS3150', 9, 110, 109, 'Digital Media Marketing', NULL, 'Internet Marketing', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (108, 'IS3103', 23, 111, 110, 'Digital Transformation and', NULL, 'ENTREPRENEURSHIP & LEADERSHIP', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (109, 'CS4248', 27, 112, 111, 'Introduction to Large Lang', NULL, 'NATURAL LANGUAGE PROCESSING', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (110, 'CS3231', 17, 113, 112, 'Theory of Computation', NULL, 'THEORY OF COMPUTATION', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (111, 'CS3241', 18, 114, 113, 'Computer Graphics', NULL, 'COMPUTER GRAPHICS', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (112, 'CS2104', 15, 115, 114, 'Programming Language C', NULL, 'PROGRAMMING LANGUAGES', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (113, 'CS3244', 1, 116, 115, 'Machine Learning', NULL, 'INTRODUCTION TO BRAIN AND MACHINE LEARNING', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (114, 'BT4240', 6, 117, 116, 'Machine Learning for Pred', NULL, 'Operations Analytics (English)', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (115, 'IS4246', 34, 118, 117, 'Smart Systems and AI Go', NULL, 'AI Security II (English)', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (116, 'BT4221', 35, 119, 118, 'Advanced Analytics with B', NULL, 'Statistical Data Science I (English)"', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (117, 'IS4246', 5, 120, 119, 'Smart Systems and AI Go', NULL, 'Artificial Intelligence for Business (English)"', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (118, 'BT4222', 33, 121, 120, 'Mining Web Data for Busin', NULL, 'Data Science in Healthcare', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (119, 'CS3240', 24, 122, 121, 'Interaction Design', NULL, 'HUMAN COMPUTER INTERACTION', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (120, 'CS2105', 20, 123, 122, 'Introduction to Computer', NULL, 'Computer Network', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (121, 'BT4222', 7, 124, 123, 'Mining Web Data for Busin', NULL, 'Social Media Analytics', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (122, 'IS4261', 8, 125, 124, 'Designing AI-driven Busin', NULL, 'Technological Innovation Management: A Pre-requisite for Successful Entrepreneurship', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (123, 'CS4222', 26, 126, 125, 'Wireless Networking', NULL, 'Wireless Communications', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (124, 'CS3241', 25, 127, 126, 'Computer Graphics', NULL, 'Interactive Visualization', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (125, 'BT4240', 32, 128, 127, 'Machine Learning for Pred', NULL, 'Pattern Recognition', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (126, 'IS3103', 3, 129, 128, 'Digital Transformation and', NULL, 'INTRODUCTION TO MANAGEMENT INFORMATION SYSTEMS(English)', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (127, 'IS4241', 7, 130, 129, 'Social Media Network Ana', NULL, 'Social Media Analytics', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (128, 'CS3244', 131, 131, 130, 'Machine Learning', NULL, 'MACHINE LEARNING', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (129, 'IT1244', 121, 132, 131, 'Artificial Intelligence: Tech', NULL, 'INTRODUCTION TO AI AND ITS APPLICATIONS', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (130, 'CS4243', 130, 133, 132, 'Computer Vision and Patte', NULL, 'Computer Vision', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (131, 'CS1231', 137, 134, 133, 'Discrete Structures', NULL, 'DISCRETE MATHEMATICS', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (132, 'CS3243', 128, 135, 134, 'Introduction to Artificial In', NULL, 'Artificial Intelligence', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (133, 'CS4243', 123, 136, 135, 'Computer Vision and Patte', NULL, 'COMPUTER VISION', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (134, 'BT3104', 141, 137, 136, 'Optimization Methods for', NULL, 'INTRODUCTION TO OPTIMIZATION FOR DATA SCIENCE', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (135, 'CS3244', 124, 138, 137, 'Machine Learning', NULL, 'MACHINE LEARNING', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (136, 'CS3231', 126, 139, 138, 'Theory of Computation', NULL, 'AUTOMATA AND FORMAL LANGUAGES', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (137, 'IS3103', 122, 140, 139, 'Digital Transformation and', NULL, 'MANAGEMENT INFORMATION SYSTEMS', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (138, 'CS5242', 135, 141, 140, 'Neural Networks and Deep', NULL, 'NEURAL NETWORK', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (139, 'IS3103', 136, 142, 141, 'Digital Transformation and', NULL, 'Global IT Management', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (140, 'CS2105', 127, 143, 142, 'Introduction to Computer', NULL, 'Computer Networks', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (141, 'CS2105', 134, 144, 143, 'Introduction to Computer', NULL, 'COMMUNICATION NETWORKS', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (142, 'CS3244', 133, 145, 144, 'Machine Learning', NULL, 'INTRODUCTION ARTIFICIAL INTELLIGENCE', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (143, 'CS3244', 139, 146, 145, 'Machine Learning', NULL, 'MATHEMATICS FOR MACHINE LEARNING', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (144, 'CS3244', 140, 147, 146, 'Machine Learning', NULL, 'STATISTICAL MACHINE LEARNING', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (145, 'CS4222', 132, 148, 147, 'Wireless Networking', NULL, 'WIRELESS AND MOBILE NETWORKS', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (146, 'CS3263', 133, 149, 148, 'Foundations of Artificial In', NULL, 'INTRODUCTION ARTIFICIAL INTELLIGENCE', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (147, 'CS4268', 138, 150, 149, 'Quantum Computing', NULL, 'QUANTUM COMPUTER', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (148, 'CS2040', 125, 151, 150, 'Data Structures and Algor', NULL, 'Data Structures', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (149, 'CS2107', 129, 152, 151, 'Introduction to Informatio', NULL, 'Information Security', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (150, 'CS3264', 140, 153, 152, 'Foundations of Machine Le', NULL, 'STATISTICAL MACHINE LEARNING', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (151, 'CS5242', 142, 154, 153, 'Neural Networks and Deep', NULL, 'DEEP LEARNING FOR VISUAL RECOGNITION', 3.00, 'School of Computing', 1);
INSERT INTO public.module_mappings (id, nus_module_code, pu_module_id, source_row_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page) OVERRIDING SYSTEM VALUE VALUES (152, 'CS3213', 100, 155, 9, 'Software Requirements Sp', NULL, 'Software Requirements and Design', 6.00, 'School of Computing', 1);


--
-- Data for Name: specializations; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.specializations (id, degree_id, name, kind, source_order) OVERRIDING SYSTEM VALUE VALUES (1, 2, 'Financial Analytics', 'specialization', 0);
INSERT INTO public.specializations (id, degree_id, name, kind, source_order) OVERRIDING SYSTEM VALUE VALUES (2, 2, 'Machine Learning-based Analytics', 'specialization', 1);
INSERT INTO public.specializations (id, degree_id, name, kind, source_order) OVERRIDING SYSTEM VALUE VALUES (3, 2, 'Marketing Analytics', 'specialization', 2);
INSERT INTO public.specializations (id, degree_id, name, kind, source_order) OVERRIDING SYSTEM VALUE VALUES (4, 3, 'AI Governance and Management', 'specialization', 0);
INSERT INTO public.specializations (id, degree_id, name, kind, source_order) OVERRIDING SYSTEM VALUE VALUES (5, 3, 'Digital Product and Platform Management', 'specialization', 1);
INSERT INTO public.specializations (id, degree_id, name, kind, source_order) OVERRIDING SYSTEM VALUE VALUES (6, 3, 'Financial Technology', 'specialization', 2);
INSERT INTO public.specializations (id, degree_id, name, kind, source_order) OVERRIDING SYSTEM VALUE VALUES (7, 4, 'Algorithms & Theory', 'focus_area', 0);
INSERT INTO public.specializations (id, degree_id, name, kind, source_order) OVERRIDING SYSTEM VALUE VALUES (8, 4, 'Artificial Intelligence', 'focus_area', 1);
INSERT INTO public.specializations (id, degree_id, name, kind, source_order) OVERRIDING SYSTEM VALUE VALUES (9, 4, 'Computer Graphics and Games', 'focus_area', 2);
INSERT INTO public.specializations (id, degree_id, name, kind, source_order) OVERRIDING SYSTEM VALUE VALUES (10, 4, 'Computer Security', 'focus_area', 3);
INSERT INTO public.specializations (id, degree_id, name, kind, source_order) OVERRIDING SYSTEM VALUE VALUES (11, 4, 'Database Systems', 'focus_area', 4);
INSERT INTO public.specializations (id, degree_id, name, kind, source_order) OVERRIDING SYSTEM VALUE VALUES (12, 4, 'Multimedia Information Retrieval', 'focus_area', 5);
INSERT INTO public.specializations (id, degree_id, name, kind, source_order) OVERRIDING SYSTEM VALUE VALUES (13, 4, 'Networking and Distributed Systems', 'focus_area', 6);
INSERT INTO public.specializations (id, degree_id, name, kind, source_order) OVERRIDING SYSTEM VALUE VALUES (14, 4, 'Parallel Computing', 'focus_area', 7);
INSERT INTO public.specializations (id, degree_id, name, kind, source_order) OVERRIDING SYSTEM VALUE VALUES (15, 4, 'Programming Languages', 'focus_area', 8);
INSERT INTO public.specializations (id, degree_id, name, kind, source_order) OVERRIDING SYSTEM VALUE VALUES (16, 4, 'Software Engineering', 'focus_area', 9);
INSERT INTO public.specializations (id, degree_id, name, kind, source_order) OVERRIDING SYSTEM VALUE VALUES (17, 5, 'Digital Product and Platform Management', 'specialization', 0);
INSERT INTO public.specializations (id, degree_id, name, kind, source_order) OVERRIDING SYSTEM VALUE VALUES (18, 5, 'Financial Technology', 'specialization', 1);
INSERT INTO public.specializations (id, degree_id, name, kind, source_order) OVERRIDING SYSTEM VALUE VALUES (19, 5, 'Intelligent Systems Solutioning', 'specialization', 2);


--
-- Data for Name: specialization_modules; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.specialization_modules (specialization_id, module_code) VALUES (1, 'BT3102');
INSERT INTO public.specialization_modules (specialization_id, module_code) VALUES (1, 'BT4012');
INSERT INTO public.specialization_modules (specialization_id, module_code) VALUES (1, 'BT4013');
INSERT INTO public.specialization_modules (specialization_id, module_code) VALUES (1, 'BT4016');
INSERT INTO public.specialization_modules (specialization_id, module_code) VALUES (1, 'BT4221');
INSERT INTO public.specialization_modules (specialization_id, module_code) VALUES (1, 'IS4226');
INSERT INTO public.specialization_modules (specialization_id, module_code) VALUES (1, 'IS4228');
INSERT INTO public.specialization_modules (specialization_id, module_code) VALUES (1, 'IS4234');
INSERT INTO public.specialization_modules (specialization_id, module_code) VALUES (1, 'IS4302');
INSERT INTO public.specialization_modules (specialization_id, module_code) VALUES (1, 'IS4303');
INSERT INTO public.specialization_modules (specialization_id, module_code) VALUES (2, 'BT3017');
INSERT INTO public.specialization_modules (specialization_id, module_code) VALUES (2, 'BT4012');
INSERT INTO public.specialization_modules (specialization_id, module_code) VALUES (2, 'BT4014');
INSERT INTO public.specialization_modules (specialization_id, module_code) VALUES (2, 'BT4221');
INSERT INTO public.specialization_modules (specialization_id, module_code) VALUES (2, 'BT4222');
INSERT INTO public.specialization_modules (specialization_id, module_code) VALUES (2, 'BT4240');
INSERT INTO public.specialization_modules (specialization_id, module_code) VALUES (2, 'BT4241');
INSERT INTO public.specialization_modules (specialization_id, module_code) VALUES (2, 'BT4301');
INSERT INTO public.specialization_modules (specialization_id, module_code) VALUES (2, 'CS3243');
INSERT INTO public.specialization_modules (specialization_id, module_code) VALUES (2, 'CS4248');
INSERT INTO public.specialization_modules (specialization_id, module_code) VALUES (2, 'IS4246');
INSERT INTO public.specialization_modules (specialization_id, module_code) VALUES (3, 'BT3017');
INSERT INTO public.specialization_modules (specialization_id, module_code) VALUES (3, 'BT4014');
INSERT INTO public.specialization_modules (specialization_id, module_code) VALUES (3, 'BT4015');
INSERT INTO public.specialization_modules (specialization_id, module_code) VALUES (3, 'BT4211');
INSERT INTO public.specialization_modules (specialization_id, module_code) VALUES (3, 'BT4212');
INSERT INTO public.specialization_modules (specialization_id, module_code) VALUES (3, 'BT4222');
INSERT INTO public.specialization_modules (specialization_id, module_code) VALUES (3, 'IS3150');
INSERT INTO public.specialization_modules (specialization_id, module_code) VALUES (3, 'IS4241');
INSERT INTO public.specialization_modules (specialization_id, module_code) VALUES (3, 'IS4262');


--
-- Name: catalog_import_batches_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.catalog_import_batches_id_seq', 1, true);


--
-- Name: catalog_issues_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.catalog_issues_id_seq', 34, true);


--
-- Name: catalog_repairs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.catalog_repairs_id_seq', 44, true);


--
-- Name: catalog_source_rows_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.catalog_source_rows_id_seq', 155, true);


--
-- Name: catalog_source_snapshots_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.catalog_source_snapshots_id_seq', 8, true);


--
-- Name: degrees_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.degrees_id_seq', 6, true);


--
-- Name: module_mappings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.module_mappings_id_seq', 152, true);


--
-- Name: partner_universities_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.partner_universities_id_seq', 5, true);


--
-- Name: pu_modules_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.pu_modules_id_seq', 142, true);


--
-- Name: specializations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.specializations_id_seq', 19, true);


--
-- PostgreSQL database dump complete
--

\unrestrict MOqgm9ZkoctfmYdWOrNk4BqhFjbCj4felQfEltmBRuG3bGnyVILzmMgmI73sn9p

