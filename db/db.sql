CREATE DATABASE workout;

CREATE TABLE users (
    id serial primary key,
    username text,
    bio text,
    password_digest text
);

CREATE TABLE workout (
    id serial primary key,
    user_id text,
    title text,
    description text
);

CREATE TABLE exercise (
    id serial primary key,
    workout_id integer,
    name text,
    reps integer,
    sets integer,
    weight numeric
);


insert into workout (user_id, title, description) values ('1', 'legs', 'only expect the worst'); --2'

insert into exercise (workout_id, name, reps, sets, weight) values ('1', 'squats', '10', '2', 100); -- 1

insert into exercise (workout_id, name, reps, sets, weight) values ('1', 'rdls', '10', '2', 100); -- 1 

-- select * from workout inner join exercise on workout.id = exercise.workout_id inner join users on workout.user_id = users.id where workout.id = 1;

select * from workout 
inner join users on workout.user_id = users.id 
inner join exercise on workout.id = exercise.workout_id
where workout.id = 1;

select * from workout
inner join exercise on workout.id = exercise.workout_id
where workout.id = 1;