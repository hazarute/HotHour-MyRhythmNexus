-- AlterTable
ALTER TABLE "reservations" ADD COLUMN "cancelledAt" TIMESTAMP(3),
ADD COLUMN "cancelSource" TEXT;
