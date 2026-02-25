-- CreateEnum
CREATE TYPE "public"."Role" AS ENUM ('USER', 'ADMIN');

-- CreateEnum
CREATE TYPE "public"."Gender" AS ENUM ('FEMALE', 'MALE');

-- CreateEnum
CREATE TYPE "public"."AuctionStatus" AS ENUM ('DRAFT', 'ACTIVE', 'SOLD', 'EXPIRED', 'CANCELLED');

-- CreateEnum
CREATE TYPE "public"."PaymentStatus" AS ENUM ('PENDING_ON_SITE', 'COMPLETED', 'NO_SHOW', 'CANCELLED');

-- CreateTable
CREATE TABLE "public"."users" (
    "id" SERIAL NOT NULL,
    "email" TEXT NOT NULL,
    "phone" TEXT NOT NULL,
    "fullName" TEXT NOT NULL,
    "gender" "public"."Gender" NOT NULL,
    "hashedPassword" TEXT NOT NULL,
    "role" "public"."Role" NOT NULL DEFAULT 'USER',
    "isVerified" BOOLEAN NOT NULL DEFAULT false,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."auctions" (
    "id" SERIAL NOT NULL,
    "title" TEXT NOT NULL,
    "description" TEXT,
    "startPrice" DECIMAL(10,2) NOT NULL,
    "floorPrice" DECIMAL(10,2) NOT NULL,
    "currentPrice" DECIMAL(10,2) NOT NULL,
    "startTime" TIMESTAMP(3) NOT NULL,
    "endTime" TIMESTAMP(3) NOT NULL,
    "dropIntervalMins" INTEGER NOT NULL DEFAULT 60,
    "dropAmount" DECIMAL(10,2) NOT NULL,
    "turboEnabled" BOOLEAN NOT NULL DEFAULT false,
    "turboTriggerMins" INTEGER NOT NULL DEFAULT 120,
    "turboDropAmount" DECIMAL(10,2) NOT NULL DEFAULT 0,
    "turboIntervalMins" INTEGER NOT NULL DEFAULT 5,
    "turboStartedAt" TIMESTAMP(3),
    "status" "public"."AuctionStatus" NOT NULL DEFAULT 'DRAFT',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "auctions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."reservations" (
    "id" SERIAL NOT NULL,
    "auctionId" INTEGER NOT NULL,
    "userId" INTEGER NOT NULL,
    "lockedPrice" DECIMAL(10,2) NOT NULL,
    "bookingCode" TEXT NOT NULL,
    "status" "public"."PaymentStatus" NOT NULL DEFAULT 'PENDING_ON_SITE',
    "reservedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "reservations_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."notifications" (
    "id" SERIAL NOT NULL,
    "userId" INTEGER NOT NULL,
    "title" TEXT NOT NULL,
    "message" TEXT NOT NULL,
    "isRead" BOOLEAN NOT NULL DEFAULT false,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "notifications_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "users_email_key" ON "public"."users"("email");

-- CreateIndex
CREATE UNIQUE INDEX "users_phone_key" ON "public"."users"("phone");

-- CreateIndex
CREATE INDEX "auctions_status_idx" ON "public"."auctions"("status");

-- CreateIndex
CREATE INDEX "auctions_endTime_idx" ON "public"."auctions"("endTime");

-- CreateIndex
CREATE UNIQUE INDEX "reservations_auctionId_key" ON "public"."reservations"("auctionId");

-- CreateIndex
CREATE UNIQUE INDEX "reservations_bookingCode_key" ON "public"."reservations"("bookingCode");

-- AddForeignKey
ALTER TABLE "public"."reservations" ADD CONSTRAINT "reservations_auctionId_fkey" FOREIGN KEY ("auctionId") REFERENCES "public"."auctions"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."reservations" ADD CONSTRAINT "reservations_userId_fkey" FOREIGN KEY ("userId") REFERENCES "public"."users"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."notifications" ADD CONSTRAINT "notifications_userId_fkey" FOREIGN KEY ("userId") REFERENCES "public"."users"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
