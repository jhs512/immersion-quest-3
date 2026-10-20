//! Account-specific catalog views; installed content and saved progress stay intact.
use crate::repository_course::{CourseManifest, COURSE_REPOSITORY};

pub fn for_account(mut course: CourseManifest, login: &str) -> CourseManifest {
    if course.repository == COURSE_REPOSITORY && !login.eq_ignore_ascii_case("jhs512") {
        course.lessons.truncate(3);
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
    fn ordinary_accounts_see_only_the_first_three_java_lessons() {
        let original = course(COURSE_REPOSITORY);
        for login in ["learner", "jhs512gh", "jhs512-other", ""] {
            let visible = for_account(original.clone(), login);
            assert_eq!(visible.lessons, original.lessons[..3]);
            assert_eq!(visible.id, original.id);
            assert_eq!(visible.lessons.iter().map(|l| l.revision.as_str()).collect::<Vec<_>>(),
                ["bash-basics-1", "vim-basics-1", "git-first-1"]);
        }
        assert_eq!(original.lessons.len(), 22, "the installed course must remain complete");
    }

    #[test]
    fn verified_github_owner_sees_the_full_java_course() {
        let original = course(COURSE_REPOSITORY);
        for login in ["jhs512", "JHS512"] {
            assert_eq!(for_account(original.clone(), login), original);
        }
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
