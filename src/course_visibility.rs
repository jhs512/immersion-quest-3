//! Account-specific catalog views; installed content and saved progress stay intact.
use crate::repository_course::{CourseManifest, COURSE_REPOSITORY};

pub fn for_account(mut course: CourseManifest, login: &str) -> CourseManifest {
    if course.repository == COURSE_REPOSITORY && !login.eq_ignore_ascii_case("jhs512") {
        let end=course.lessons.iter().position(|lesson|lesson.repository=="jhs512/mq3-lesson-redesigned-git-remote").map(|index|index+1).unwrap_or(3);
        course.lessons.truncate(end);
    }
    course
}

#[cfg(test)]
mod tests {
    use super::*;

    fn course(repository: &str) -> CourseManifest {
        CourseManifest::parse(crate::bundled_courses::course_source(repository).unwrap()).unwrap()
    }

    #[test]
    fn ordinary_accounts_see_java_lessons_through_remote() {
        let original = course(COURSE_REPOSITORY);
        for login in ["learner", "jhs512gh", "jhs512-other", ""] {
            let visible = for_account(original.clone(), login);
            let end = original.lessons.iter().position(|lesson| lesson.repository.ends_with("-git-remote")).unwrap() + 1;
            assert_eq!(visible.lessons, original.lessons[..end]);
            assert_eq!(visible.id, original.id);
            assert!(visible.lessons.last().unwrap().repository.ends_with("-git-remote"));
            assert!(!visible.lessons.iter().any(|lesson| lesson.repository.ends_with("-github-pr")));
        }
        assert_eq!(original.lessons.len(), 24, "the installed course must remain complete");
    }

    #[test]
    fn verified_github_owner_sees_the_full_java_course() {
        let original = course(COURSE_REPOSITORY);
        for login in ["jhs512", "JHS512"] {
            assert_eq!(for_account(original.clone(), login), original);
        }
    }

    #[test]
    fn content_revisions_do_not_change_the_visible_lesson_boundary() {
        let mut revised=course(COURSE_REPOSITORY);
        for lesson in &mut revised.lessons {lesson.revision.push_str("-revised");}
        let end = revised.lessons.iter().position(|lesson| lesson.repository.ends_with("-git-remote")).unwrap() + 1;
        assert_eq!(for_account(revised.clone(),"learner").lessons,revised.lessons[..end]);
    }

    #[test]
    fn other_courses_are_visible_in_full_to_every_account() {
        for repository in crate::bundled_courses::REPOSITORIES.into_iter().filter(|r| *r != COURSE_REPOSITORY) {
            let original = course(repository);
            for login in ["learner", "jhs512"] {
                assert_eq!(for_account(original.clone(), login), original);
            }
        }
    }
}
