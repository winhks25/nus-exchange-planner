export type Degree = { name: string; degree: string };
export type University = { name: string; country: string };
export type Catalog = { degrees: Degree[]; universities: University[] };
export type Recommendation = { university: string; country: string; module_count: number };
export type Recommendations = { degree: string; recommendations: Recommendation[] };
export type Course = { code: string; title?: string; units?: number };
export type Mapping = { nus_course: Course; partner_course: Course };
export type MappingResult = { degree: string; university: string; distinct_nus_module_count: number; mappings: Mapping[] };
