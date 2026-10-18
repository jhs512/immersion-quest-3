use dioxus::prelude::*;
use molip_quest::task_interaction::Interaction;

#[component]
pub fn InteractionEditor(interaction: Interaction, value: String, disabled: bool, onchange: EventHandler<String>) -> Element {
    let bridge_value=value.clone();
    let content=match interaction {
        Interaction::Choice { options, .. } => rsx! {
            fieldset { class: "answer-interaction", disabled,
                legend { "답을 골라요" }
                for option in options {
                    label { class: "answer-option", key: "{option.id}", "data-option-id":option.id.clone(),
                        input { r#type: "radio", name: "step-choice", value: option.id.clone(), checked: value == option.id,
                            onchange: move |_| onchange.call(option.id.clone()) }
                        span { "{option.text}" }
                    }
                }
            }
        },
        Interaction::Fill { .. } => rsx! {
            label { class: "answer-interaction", span { "빈칸에 들어갈 답" }
                input { r#type: "text", aria_label: "빈칸 답안", value, disabled, oninput: move |event| onchange.call(event.value()) }
            }
        },
        Interaction::FillFields {fields}=>{
            let values=serde_json::from_str::<std::collections::BTreeMap<String,String>>(&value).unwrap_or_default();
            rsx! {fieldset {class:"answer-interaction",disabled,
                legend {"각 상태를 적어요"}
                for field in fields {
                    label {key:"{field.id}",span {"{field.label}"}
                        input {r#type:"text",aria_label:field.label.clone(),"data-answer-field":field.id.clone(),value:values.get(&field.id).cloned().unwrap_or_default(),disabled,
                            oninput:{let mut next=values.clone();move |event|{next.insert(field.id.clone(),event.value());onchange.call(serde_json::to_string(&next).unwrap());}}
                        }
                    }
                }
            }}
        },
        Interaction::Order { options, .. } => {
            let selected = serde_json::from_str::<Vec<String>>(&value).unwrap_or_default();
            rsx! {
                fieldset { class: "answer-interaction", disabled,
                    legend { "조각을 골라 순서를 만들어요" }
                    div { class: "answer-pool",
                        for option in options.iter().filter(|o| !selected.contains(&o.id)) {
                            button { r#type: "button", key: "{option.id}", onclick: {let mut next = selected.clone(); next.push(option.id.clone()); move |_| onchange.call(serde_json::to_string(&next).unwrap())}, "{option.text}" }
                        }
                    }
                    ol { class: "answer-order",
                        for (index, id) in selected.iter().enumerate() {
                            li { key: "{id}", "data-option-id":id.clone(),
                                span { {options.iter().find(|o| o.id == *id).map(|o| o.text.as_str()).unwrap_or("알 수 없는 조각")} }
                                button { r#type: "button", disabled: index == 0, aria_label: "조각 위로", onclick: {let mut next = selected.clone(); if index > 0 {next.swap(index, index - 1);} move |_| onchange.call(serde_json::to_string(&next).unwrap())}, "↑" }
                                button { r#type: "button", disabled: index + 1 == selected.len(), aria_label: "조각 아래로", onclick: {let mut next = selected.clone(); if index + 1 < next.len() {next.swap(index, index + 1);} move |_| onchange.call(serde_json::to_string(&next).unwrap())}, "↓" }
                                button { r#type: "button", aria_label: "조각 빼기", onclick: {let mut next = selected.clone(); next.remove(index); move |_| onchange.call(serde_json::to_string(&next).unwrap())}, "빼기" }
                            }
                        }
                    }
                }
            }
        }
    };
    rsx! {input {r#type:"hidden",class:"answer-state-bridge",value:bridge_value,oninput:move |event|onchange.call(event.value())}{content}}
}
