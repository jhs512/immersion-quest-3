export function lessonTarget(search) {
  const pairs = [...new URLSearchParams(search)];
  if (pairs.length !== 2 || new Set(pairs.map(([key]) => key)).size !== 2 || pairs.some(([key]) => !['course','lesson'].includes(key))) throw Error('코스와 수업 링크를 확인하세요.');
  const params = new URLSearchParams(search), course = params.get('course'), lesson = params.get('lesson');
  if (!course || course.length > 160 || !/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(course) || course.split('/').some(part => ['.','..'].includes(part)) || !lesson || lesson.length > 160 || !/^[A-Za-z0-9_-]+$/.test(lesson)) throw Error('코스와 수업 링크를 확인하세요.');
  const app = new URL('molipquest://open'); app.searchParams.set('course',course); app.searchParams.set('lesson',lesson);
  return {course,lesson,app:app.href};
}
