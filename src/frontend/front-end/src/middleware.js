export {default} from 'next-auth/middleware';

import { NextResponse } from 'next/server';
import { getToken } from 'next-auth/jwt';

export const config = {
    matcher: ['/dashboard', '/homepage'],
};

export async function middleware(req) {
    const session = await getToken({ req, secret: process.env.NEXTAUTH_SECRET });
    if (!session && req.nextUrl.pathname.startsWith('/dashboard')) {
        return NextResponse.redirect(new URL('/login', req.url));
    }
    if (!session && req.nextUrl.pathname.startsWith('/homepage')) {
        return NextResponse.redirect(new URL('/login', req.url));
    }

    return NextResponse.next();
}