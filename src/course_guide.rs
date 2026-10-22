//! Learner-safe overview derived only from the installed, validated snapshot.
use crate::content_updates::Snapshot;
use serde::{Serialize,Deserialize};
#[derive(Clone,Debug,PartialEq,Serialize,Deserialize)]
pub struct CourseGuide {
    pub title:String,pub description:String,pub objectives:Vec<String>,pub scope_note:String,
    pub fingerprint:String,pub lessons:Vec<GuideLesson>,
}
#[derive(Clone,Debug,PartialEq,Serialize,Deserialize)]
pub struct GuideLesson {
    pub title:String,pub description:String,pub objectives:Vec<String>,pub story:Vec<String>,
    pub prerequisites:Vec<String>,pub strategy:String,
}
impl CourseGuide {
    pub fn from_snapshot(snapshot:&Snapshot)->Self {
        let course=snapshot.course();
        let lessons=course.lessons.iter().map(|reference|{
            let lesson=snapshot.lesson(reference).expect("validated snapshot owns every lesson");
            let mut story=Vec::new();
            for unit in lesson.chapters.iter().flat_map(|chapter|&chapter.units) {
                if !unit.premise.trim().is_empty()&&unit.premise!=lesson.description&&!story.contains(&unit.premise){story.push(unit.premise.clone());}
            }
            GuideLesson{title:lesson.title.clone(),description:lesson.description.clone(),objectives:lesson.objectives.clone(),story,
                prerequisites:reference.prerequisites.iter().filter_map(|id|course.lessons.iter().find(|r|&r.id==id).map(|r|r.title.clone())).collect(),
                strategy:lesson.learning_strategy.clone()}
        }).collect();
        Self{title:course.title.clone(),description:course.description.clone(),objectives:course.objectives.clone(),scope_note:course.scope_note.clone(),fingerprint:snapshot.fingerprint(),lessons}
    }
    /// Same source and targets as the document; no task answers or private PRDs.
    pub fn narration(&self,only_lesson:Option<usize>)->Vec<serde_json::Value> {
        let mut actions=Vec::new();
        let mut say=|text:String,target:String|actions.push(serde_json::json!({"action":"say","text":text,"target":target}));
        if only_lesson.is_none(){
            say(format!("{}의 목표와 전체 흐름을 살펴봐요.",self.title),"#course-guide-summary".into());
            for (i,goal) in self.objectives.iter().enumerate(){say(goal.clone(),format!("#course-guide-goal-{i}"));}
            if !self.scope_note.is_empty(){say(self.scope_note.clone(),"#course-guide-scope".into());}
        }
        for (i,lesson) in self.lessons.iter().enumerate().filter(|(i,_)|only_lesson.is_none_or(|only|only==*i)) {
            let target=format!("#course-guide-lesson-{i}");
            say(format!("{} 수업이에요. {}",lesson.title,lesson.description),target.clone());
            for (j,goal) in lesson.objectives.iter().enumerate() {say(goal.clone(),format!("{target}-goal-{j}"));}
            for (j,premise) in lesson.story.iter().enumerate() {say(premise.clone(),format!("{target}-story-{j}"));}
        }
        actions
    }
}
