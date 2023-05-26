with all_questions as (
    select 
        id,
        position,
        question_type,
        body->>'fr' as question_title
    from decidim_forms_questions
    where decidim_questionnaire_id = QUESTIONNAIRE_ID
        and question_type != 'separator'
    order by position
), simple_questions as (
    select *,
        '{}'::text[] as "possible_answers",
        '{}'::text[] as "sub_affirmations"
    from all_questions
    where question_type like ANY('{short_answer,long_answer, single_option}'::text[])
), multiple_option as (
    select 
        all_questions.*,
        array_agg(parsed_body) as "possible_answers",
        '{}'::text[] as "sub_affirmations"
    from all_questions
        join decidim_forms_answer_options on decidim_forms_answer_options.decidim_question_id = all_questions.id,
        lateral (select concat('', decidim_forms_answer_options.body->>'fr') as parsed_body) _
    where question_type like ANY('{multiple_option}'::text[])
    group by position, question_type, question_title, all_questions.id
), matrix_questions as (
    select
        all_questions.*,
        array_agg(distinct parsed_body) as "possible_answers",
        array_agg(distinct parsed_matrix_rows) as "sub_affirmations"
    from all_questions
        join decidim_forms_answer_options on decidim_forms_answer_options.decidim_question_id = all_questions.id
        join decidim_forms_question_matrix_rows on decidim_forms_question_matrix_rows.decidim_question_id = all_questions.id,
            lateral (select concat(' ', decidim_forms_answer_options.body->>'fr') as parsed_body) _,
            lateral (select concat(' ', decidim_forms_question_matrix_rows.body->>'fr') as parsed_matrix_rows) __
    where question_type like ANY('{matrix_single, matrix_multiple}'::text[])
    group by all_questions.position, question_type, question_title, all_questions.id
)
select * from multiple_option
union all select * from simple_questions 
union all select * from matrix_questions
order by position