import { NextAuthOptions } from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'
import bcrypt from "bcrypt";

export const authOptions = {
    providers: [
        CredentialsProvider({
          name: "credentials",
          credentials: {
            // username: { label: 'Username', type: 'text' },
            // password: {  label: 'Password', type: 'password' }
          },
          
          // Takes in the email and password and checks if the user exists
          // if the user exists, it matches the password with the encrypted one stored in the DB
          // returns the user if everything is successful and takes the user to the dashboard
          async authorize(req)  {
            const email = credentials.email;
            const password = credentials.password;
            try {
              const db = await connectMongoDB();
              const user = await User.findOne({ email });
  
              console.log("this is the user", user);
              if (!user) {
                return null; // Return null when user is not found
              }
  
              console.log(password, user.password);
              const passwordsMatch = await bcrypt.compare(password, user.password);
    
              if (!passwordsMatch) {
                return null; // Return null when passwords do not match
              }
  
              // Return the user object when authentication is successful
              console.log("this is thee user: ", user);
              return user;
            } catch (error) {
              console.log("Error: ", error);
              return null; // Return null in case of an error
            }
          },
        }),
      ],
      callbacks: {
        async jwt({token, user}) {
          // console.log("jwt callback", {token, user});
          if (user) {
            token.email = user.email;
          }
          return token;
        },
        async session({ session}) {
          // console.log("session callback", {session});
          if (session.user) {
            const user = await User.findOne({ email: session.user.email });
            // session.user = user; // Update the session user object
            session.user.test = user.test;
          }
          return session;
        }
      },
      secret: process.env.NEXTAUTH_SECRET,
      session: {
        strategy: "jwt",
      },
      pages: {
        signIn: "/login",
      },
    };
