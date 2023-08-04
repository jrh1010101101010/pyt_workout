const bcrypt = require('bcrypt')
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://tgazdhfywzhmtmauqukw.supabase.co'
const supabaseKey = process.env.SUPABASE_KEY
const supabase = createClient(supabaseUrl, supabaseKey)

const password = hannah 
const genSalt = 10

bcrypt.hash(password, saltRounds, async (err, hash) => {
  if (err) {
    console.error('Error generating hash:', err);
    return;
  }

  // Create the user in Supabase
  const { user, error } = await supabase.auth.signUp({
    email: 'user@example.com',
    password: hash // Store the hashed password in the user record
  });

  if (error) {
    console.error('Error creating user:', error);
    return;
  }

  console.log('User created:', user);
});


