import type { Mapping } from "@/lib/types";
function CourseDetails({ course }: { course: Mapping["nus_course"] }) {
  return <div className="course"><strong>{course.code}</strong>{course.title && <span>{course.title}</span>}{course.units !== undefined && <small>{course.units} units</small>}</div>;
}
export default function MappingRows({ mappings }: { mappings: Mapping[] }) {
  return <div className="mapping-list">{mappings.map((row, index) => <div className="mapping-row" key={`${row.nus_course.code}-${row.partner_course.code}-${index}`}><CourseDetails course={row.nus_course}/><span className="maps-to" aria-label="maps to">→</span><CourseDetails course={row.partner_course}/></div>)}</div>;
}
