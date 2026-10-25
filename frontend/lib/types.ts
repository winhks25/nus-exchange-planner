export type PageState = "loading-catalog" | "idle" | "loading" | "error";

export type Faculty = {
  id: number;
  name: string;
};

export type Degree = {
  name: string;
  degree: string;
  faculty_ids: number[];
};

export type University = {
  id: number | null;
  name: string;
  country: string;
  city: string | null;
  continent: string | null;
  faculty_ids: number[];
  image: string | null;
  website: string | null;
  image_attribution: string | null;
};

export type Catalog = {
  faculties: Faculty[];
  degrees: Degree[];
  universities: University[];
};

export type Recommendation = {
  university: string;
  country: string;
  partner_module_count: number;
  distinct_nus_module_count: number;
  mapping_count: number;
};

export type Recommendations = {
  degree: string;
  recommendations: Recommendation[];
};

export type Course = {
  code: string;
  title?: string;
  units?: number;
};

export type Mapping = {
  nus_course: Course;
  partner_course: Course;
};

export type MappingResult = {
  degree: string;
  university: string;
  partner_module_count: number;
  distinct_nus_module_count: number;
  mappings: Mapping[];
};
