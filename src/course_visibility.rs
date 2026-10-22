//! Every account sees the complete published course and can choose any lesson.
use crate::repository_course::CourseManifest;

pub fn for_account(course: CourseManifest, _login: &str) -> CourseManifest {
    course
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn every_account_sees_every_published_lesson_in_all_basic_courses() {
        for repository in crate::bundled_courses::REPOSITORIES {
            let original = CourseManifest::parse(crate::bundled_courses::course_source(repository).unwrap()).unwrap();
            for login in ["learner", "jhs512gh", "jhs512-other", "", "jhs512", "JHS512"] {
                assert_eq!(for_account(original.clone(), login), original,
                    "{login:?} must see the full published course {repository}");
            }
        }
    }

    #[test]
    fn new_lessons_and_revisions_are_not_cut_off_at_the_old_git_boundary() {
        let mut revised = CourseManifest::parse(crate::bundled_courses::course_source(crate::repository_course::COURSE_REPOSITORY).unwrap()).unwrap();
        for lesson in &mut revised.lessons { lesson.revision.push_str("-revised"); }
        assert!(revised.lessons.iter().any(|lesson| lesson.repository.ends_with("-github-pr")));
        assert_eq!(for_account(revised.clone(), "learner"), revised);
        revised.lessons.retain(|lesson| !lesson.repository.ends_with("-git-remote"));
        assert_eq!(for_account(revised.clone(), "learner"), revised,
            "removing a boundary lesson must never fall back to a three-lesson limit");
    }
}
